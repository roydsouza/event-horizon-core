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

func (pm *ProcessManager) Start(ctx context.Context) error {
	pm.mu.Lock()
	if pm.status == StatusRunning || pm.status == StatusStarting {
		s := pm.status
		pm.mu.Unlock()
		return fmt.Errorf("server is already %s", s)
	}
	pm.status = StatusStarting
	model := pm.modelPath
	pm.mu.Unlock()

	log.Printf("[Supervisor] Starting MLX server for model: %s on port %d", model, pm.port)

	args := []string{"run", "mlx_lm.server",
		"--model", pm.modelPath,
		"--port", fmt.Sprintf("%d", pm.port),
		"--prompt-cache-size", "2048",
	}

	if draft := os.Getenv("MLX_DRAFT_MODEL"); draft != "" {
		log.Printf("[Supervisor] Enabling Speculative Decoding with draft model: %s", draft)
		args = append(args, "--draft-model", draft)
	}

	pm.cmd = exec.CommandContext(ctx, "uv", args...)
	pm.cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}

	pm.cmd.Stdout = os.Stdout
	pm.cmd.Stderr = os.Stderr

	if err := pm.cmd.Start(); err != nil {
		pm.mu.Lock()
		pm.status = StatusError
		pm.mu.Unlock()
		return fmt.Errorf("failed to start mlx_lm.server: %w", err)
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

	err := pm.WaitUntilHealthy(ctx)
	if err == nil {
		pm.mu.Lock()
		pm.status = StatusRunning
		pm.mu.Unlock()
	}
	return err
}

func (pm *ProcessManager) WaitUntilHealthy(ctx context.Context) error {
	healthURL := fmt.Sprintf("http://127.0.0.1:%d/health", pm.port)
	log.Printf("[Supervisor] Waiting for HTTP health on %s...", healthURL)

	ticker := time.NewTicker(500 * time.Millisecond)
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
			return fmt.Errorf("timeout waiting for server health on %s", healthURL)
		case <-ticker.C:
			resp, err := client.Get(healthURL)
			if err == nil {
				resp.Body.Close()
				if resp.StatusCode == http.StatusOK {
					log.Printf("[Supervisor] Server is healthy on port %d", pm.port)
					return nil
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

	if err := pm.Stop(); err != nil {
		return fmt.Errorf("failed to stop old model: %w", err)
	}

	pm.mu.Lock()
	pm.modelPath = newModelPath
	pm.mu.Unlock()

	return pm.Start(ctx)
}

func (pm *ProcessManager) Stop() error {
	if pm.cmd == nil || pm.cmd.Process == nil {
		return nil
	}

	log.Printf("[Supervisor] Stopping server process group...")

	err := syscall.Kill(-pm.cmd.Process.Pid, syscall.SIGKILL)
	if err != nil {
		return fmt.Errorf("failed to kill process group: %w", err)
	}

	pm.mu.Lock()
	pm.status = StatusStopped
	pm.mu.Unlock()
	return nil
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
