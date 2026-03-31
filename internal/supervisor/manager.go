package supervisor

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"
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

type ProcessManager struct {
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

func (pm *ProcessManager) CurrentModel() string {
	return pm.modelPath
}

func (pm *ProcessManager) Start(ctx context.Context) error {
	if pm.status == StatusRunning || pm.status == StatusStarting {
		return fmt.Errorf("server is already %s", pm.status)
	}

	pm.status = StatusStarting
	log.Printf("[Supervisor] Starting MLX server for model: %s on port %d", pm.modelPath, pm.port)

	// Create command: uv run mlx_lm.server --model <model> --port <port>
	// Advanced optimization: Injects --prompt-cache-size and --max-tokens to optimize Metal on M5
	args := []string{"run", "mlx_lm.server",
		"--model", pm.modelPath,
		"--port", fmt.Sprintf("%d", pm.port),
		"--prompt-cache-size", "2048", // Prefix Caching enabled by default
	}

	// Speculative Decoding: If a draft model is available (e.g. 1B for a 3B/7B primary), inject it.
	// For now, we'll check for a conventionally named draft model or a specific env var.
	if draft := os.Getenv("MLX_DRAFT_MODEL"); draft != "" {
		log.Printf("[Supervisor] Enabling Speculative Decoding with draft model: %s", draft)
		args = append(args, "--draft-model", draft)
	}

	pm.cmd = exec.CommandContext(ctx, "uv", args...)
	pm.cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	
	pm.cmd.Stdout = os.Stdout
	pm.cmd.Stderr = os.Stderr

	if err := pm.cmd.Start(); err != nil {
		pm.status = StatusError
		return fmt.Errorf("failed to start mlx_lm.server: %w", err)
	}

	// Wait for process in a goroutine
	go func() {
		err := pm.cmd.Wait()
		pm.status = StatusStopped
		if err != nil {
			log.Printf("[Supervisor] Server process exited with error: %v", err)
		} else {
			log.Printf("[Supervisor] Server process exited cleanly")
		}
	}()

	return pm.WaitUntilHealthy(ctx)
}

func (pm *ProcessManager) WaitUntilHealthy(ctx context.Context) error {
	addr := fmt.Sprintf("127.0.0.1:%d", pm.port)
	log.Printf("[Supervisor] Waiting for port %s to become healthy...", addr)
	
	ticker := time.NewTicker(200 * time.Millisecond)
	defer ticker.Stop()

	timeoutCtx, cancel := context.WithTimeout(ctx, 90*time.Second)
	defer cancel()

	for {
		select {
		case <-timeoutCtx.Done():
			pm.status = StatusError
			return fmt.Errorf("timeout waiting for server health on %s", addr)
		case <-ticker.C:
			// Simple TCP check to see if the server is listening
			conn, err := net.DialTimeout("tcp", addr, 100*time.Millisecond)
			if err == nil {
				conn.Close()
				pm.status = StatusRunning
				log.Printf("[Supervisor] Server is healthy on port %d", pm.port)
				return nil
			}
		}
	}
}

func (pm *ProcessManager) SwitchModel(ctx context.Context, newModelPath string) error {
	log.Printf("[Supervisor] Hot-Swapping Model: %s -> %s", pm.modelPath, newModelPath)
	
	if err := pm.Stop(); err != nil {
		return fmt.Errorf("failed to stop old model: %w", err)
	}

	pm.modelPath = newModelPath
	return pm.Start(ctx)
}

func (pm *ProcessManager) Stop() error {
	if pm.cmd == nil || pm.cmd.Process == nil {
		return nil
	}

	log.Printf("[Supervisor] Stopping server process group...")
	
	// Send SIGKILL to the entire process group (negative PID)
	err := syscall.Kill(-pm.cmd.Process.Pid, syscall.SIGKILL)
	if err != nil {
		return fmt.Errorf("failed to kill process group: %w", err)
	}

	pm.status = StatusStopped
	return nil
}

func (pm *ProcessManager) GetStatus() ServerStatus {
	return pm.status
}
