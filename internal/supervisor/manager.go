package supervisor

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"sync"
	"syscall"
	"time"
)

type ServerStatus string

const (
	StatusStopped  ServerStatus = "stopped"
	StatusStarting ServerStatus = "starting"
	StatusRunning  ServerStatus = "running"
	StatusError    ServerStatus = "error"
)

// ErrSwapInProgress is returned by TrySwitchModel when a model swap is already running.
var ErrSwapInProgress = fmt.Errorf("model swap already in progress")

// SwapMetrics captures sub-millisecond durations for a model hot-swap event.
type SwapMetrics struct {
	Timestamp      string  // ISO8601
	FromModel      string  // Previous model
	ToModel        string  // New model
	KillDuration   float64 // ms: KillStart -> ProcessExit
	StartupDelay   float64 // ms: UvStart -> FirstHealthCheck (Proxy for Python/uv overhead)
	WeightLoading  float64 // ms: FirstHealthCheck -> Ready (Proxy for Disk -> Metal weight load)
	TotalDuration  float64 // ms: KillStart -> Ready
	PythonOverhead float64 // %: (StartupDelay / TotalDuration) * 100
}

func appendMetricsToCSV(m SwapMetrics) error {
	path := "../../benchmarks/swap_latency.csv" // Relative to internal/supervisor
	// Check if we are running from root
	if _, err := os.Stat("benchmarks"); err == nil {
		path = "benchmarks/swap_latency.csv"
	}
	firstRun := false
	if _, err := os.Stat(path); os.IsNotExist(err) {
		firstRun = true
	}

	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer f.Close()

	if firstRun {
		header := "timestamp,from_model,to_model,kill_ms,python_startup_ms,weight_load_ms,total_ms,python_percent\n"
		f.WriteString(header)
	}

	line := fmt.Sprintf("%s,%s,%s,%.2f,%.2f,%.2f,%.2f,%.2f\n",
		m.Timestamp, m.FromModel, m.ToModel, m.KillDuration, m.StartupDelay, m.WeightLoading, m.TotalDuration, m.PythonOverhead)
	_, err = f.WriteString(line)
	return err
}

type ProcessManager struct {
	swapMu     sync.Mutex   // serializes hot-swaps; one swap at a time
	mu         sync.RWMutex // protects modelPath and status field reads/writes
	cmd        *exec.Cmd
	modelPath  string
	port       int
	status     ServerStatus
	cancelFunc context.CancelFunc
}

func NewProcessManager(modelPath string, port int) *ProcessManager {
	return &ProcessManager{
		modelPath: modelPath,
		port:      port,
		status:    StatusStopped,
	}
}

func (pm *ProcessManager) Start(ctx context.Context) (time.Time, time.Time, error) {
	var uvStart, firstHealth time.Time
	pm.mu.Lock()
	if pm.status == StatusRunning || pm.status == StatusStarting {
		s := pm.status
		pm.mu.Unlock()
		return uvStart, firstHealth, fmt.Errorf("server is already %s", s)
	}
	pm.status = StatusStarting
	model := pm.modelPath
	pm.mu.Unlock()

	log.Printf("[Supervisor] Starting MLX server for model: %s on port %d", model, pm.port)

	args := []string{"run", "mlx_lm.server",
		"--model", pm.modelPath,
		"--port", fmt.Sprintf("%d", pm.port),
		"--prompt-cache-size", "512",
	}

	if draft := os.Getenv("MLX_DRAFT_MODEL"); draft != "" {
		log.Printf("[Supervisor] Enabling Speculative Decoding with draft model: %s", draft)
		args = append(args, "--draft-model", draft)
	}

	pm.cmd = exec.CommandContext(ctx, "uv", args...)
	pm.cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}

	pm.cmd.Stdout = os.Stdout
	pm.cmd.Stderr = os.Stderr

	uvStart = time.Now()
	if err := pm.cmd.Start(); err != nil {
		pm.mu.Lock()
		pm.status = StatusError
		pm.mu.Unlock()
		return uvStart, firstHealth, fmt.Errorf("failed to start mlx_lm.server: %w", err)
	}

	go func() {
		err := pm.cmd.Wait()
		pm.mu.Lock()
		pm.status = StatusStopped
		pm.mu.Unlock()
		if err != nil {
			log.Printf("[Supervisor] Server process exited with error: %v", err)
		} else {
			log.Printf("[Supervisor] Server process exited cleanly")
		}
	}()

	_, firstHealth, err := pm.WaitUntilHealthy(ctx)
	if err == nil {
		pm.mu.Lock()
		pm.status = StatusRunning
		pm.mu.Unlock()
	}
	return uvStart, firstHealth, err
}

func (pm *ProcessManager) WaitUntilHealthy(ctx context.Context) (time.Time, time.Time, error) {
	var firstHealth time.Time
	healthURL := fmt.Sprintf("http://127.0.0.1:%d/health", pm.port)
	log.Printf("[Supervisor] Waiting for HTTP health on %s...", healthURL)

	ticker := time.NewTicker(200 * time.Millisecond) // Reduced from 500ms for tighter instrumentation
	defer ticker.Stop()

	timeoutCtx, cancel := context.WithTimeout(ctx, 120*time.Second)
	defer cancel()

	client := &http.Client{Timeout: 400 * time.Millisecond}

	for {
		select {
		case <-timeoutCtx.Done():
			pm.mu.Lock()
			pm.status = StatusError
			pm.mu.Unlock()
			return time.Now(), firstHealth, fmt.Errorf("timeout waiting for server health on %s", healthURL)
		case <-ticker.C:
			if firstHealth.IsZero() {
				firstHealth = time.Now()
			}
			resp, err := client.Get(healthURL)
			if err == nil {
				resp.Body.Close()
				if resp.StatusCode == http.StatusOK {
					log.Printf("[Supervisor] Server is healthy on port %d", pm.port)
					return time.Now(), firstHealth, nil
				}
			}
		}
	}
}

// SwitchModel swaps the active model. Blocks until any in-progress swap completes.
// Use TrySwitchModel if you need non-blocking behaviour (e.g. explicit /v1/model/swap API).
func (pm *ProcessManager) SwitchModel(ctx context.Context, newModelPath string) error {
	pm.swapMu.Lock()
	defer pm.swapMu.Unlock()
	return pm.doSwitch(ctx, newModelPath)
}

// TrySwitchModel is like SwitchModel but returns ErrSwapInProgress immediately
// if a swap is already running, rather than blocking.
func (pm *ProcessManager) TrySwitchModel(ctx context.Context, newModelPath string) error {
	if !pm.swapMu.TryLock() {
		return ErrSwapInProgress
	}
	defer pm.swapMu.Unlock()
	return pm.doSwitch(ctx, newModelPath)
}

// doSwitch is the shared implementation; callers must hold swapMu.
func (pm *ProcessManager) doSwitch(ctx context.Context, newModelPath string) error {
	pm.mu.RLock()
	current := pm.modelPath
	pm.mu.RUnlock()

	if current == newModelPath {
		log.Printf("[Supervisor] Model %s already loaded, skipping redundant swap", newModelPath)
		return nil
	}

	log.Printf("[Supervisor] Hot-Swapping Model: %s -> %s", current, newModelPath)
	killStart := time.Now()

	exitTime, err := pm.StopWithTime()
	if err != nil {
		return fmt.Errorf("failed to stop old model: %w", err)
	}

	pm.mu.Lock()
	pm.modelPath = newModelPath
	pm.mu.Unlock()

	uvStart, firstHealth, err := pm.Start(ctx)
	if err != nil {
		return err
	}
	readyTime := time.Now()

	// Capture Metrics
	metrics := SwapMetrics{
		Timestamp:      readyTime.Format(time.RFC3339),
		FromModel:      current,
		ToModel:        newModelPath,
		KillDuration:   float64(exitTime.Sub(killStart).Microseconds()) / 1000.0,
		StartupDelay:   float64(firstHealth.Sub(uvStart).Microseconds()) / 1000.0,
		WeightLoading:  float64(readyTime.Sub(firstHealth).Microseconds()) / 1000.0,
		TotalDuration:  float64(readyTime.Sub(killStart).Microseconds()) / 1000.0,
		PythonOverhead: (float64(firstHealth.Sub(uvStart).Nanoseconds()) / float64(readyTime.Sub(killStart).Nanoseconds())) * 100.0,
	}

	log.Printf("[Experiment E1] Swap Complete. Python Overhead: %.2f%% (Total: %.2fs)", metrics.PythonOverhead, metrics.TotalDuration/1000.0)
	if err := appendMetricsToCSV(metrics); err != nil {
		log.Printf("[WARNING] Failed to log swap metrics: %v", err)
	}

	return nil
}

func (pm *ProcessManager) Stop() error {
	_, err := pm.StopWithTime()
	return err
}

func (pm *ProcessManager) StopWithTime() (time.Time, error) {
	if pm.cmd == nil || pm.cmd.Process == nil {
		return time.Now(), nil
	}

	log.Printf("[Supervisor] Stopping server process group...")

	err := syscall.Kill(-pm.cmd.Process.Pid, syscall.SIGKILL)
	if err != nil {
		return time.Now(), fmt.Errorf("failed to kill process group: %w", err)
	}

	// Simple wait for termination to ensure clean release of Metal resources
	deadline := time.Now().Add(5 * time.Second)
	for time.Now().Before(deadline) {
		pm.mu.RLock()
		s := pm.status
		pm.mu.RUnlock()
		if s == StatusStopped {
			break
		}
		time.Sleep(50 * time.Millisecond)
	}

	pm.mu.Lock()
	pm.status = StatusStopped
	pm.mu.Unlock()
	return time.Now(), nil
}

func (pm *ProcessManager) CurrentModel() string {
	pm.mu.RLock()
	defer pm.mu.RUnlock()
	return pm.modelPath
}

func (pm *ProcessManager) GetStatus() ServerStatus {
	pm.mu.RLock()
	defer pm.mu.RUnlock()
	return pm.status
}
