package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"github.com/roydsouza/event-horizon-core/internal/server"
	"github.com/roydsouza/event-horizon-core/internal/supervisor"
)

func main() {
	ring := server.NewEventRingBuffer(200, slog.NewJSONHandler(os.Stdout, nil))
	slog.SetDefault(slog.New(ring))

	// 1. Initialize Supervisor for MLX (Target: port 8080)
	// In the final version, the model path would come from environment or persistent config.
	modelPath := "mlx-community/Hermes-3-Llama-3.1-8B-4bit"
	pm := supervisor.NewProcessManager(modelPath, 8080)

	// 2. Start Supervisor in the background so the HTTP server can start immediately
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go func() {
		if _, _, err := pm.Start(ctx); err != nil {
			slog.Error("Background supervisor startup failed", "error", err)
		}
	}()

	// 3. Initialize HTTP Daemon (Listening on port 8000 per PORTS.md)
	s := server.NewEventHorizonServer(pm, 8000, ring)

	// 4. Handle OS Signals for graceful shutdown
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		sig := <-sigs
		slog.Info("Received signal. Initiating shutdown", "signal", sig)
		
		// Stop the server
		// We'll trust the context cancellation and supervisor cleanup for the child processes
		pm.Stop()
		cancel()
		
		os.Exit(0)
	}()

	// 5. Start HTTP Server (Blocking)
	if err := s.Start(); err != nil {
		slog.Error("Failed to start HTTP server", "error", err)
		os.Exit(1)
	}
}
