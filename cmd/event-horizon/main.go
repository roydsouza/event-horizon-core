package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/roydsouza/event-horizon-core/internal/server"
	"github.com/roydsouza/event-horizon-core/internal/supervisor"
)

func main() {
	// 1. Initialize Supervisor for MLX (Target: port 8080)
	// In the final version, the model path would come from environment or persistent config.
	modelPath := "mlx-community/Llama-3.2-3B-Instruct-4bit"
	pm := supervisor.NewProcessManager(modelPath, 8080)

	// 2. Start Supervisor
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	if err := pm.Start(ctx); err != nil {
		log.Fatalf("[Main] Failed to start supervisor: %v", err)
	}

	// 3. Initialize HTTP Daemon (Listening on port 8000 per PORTS.md)
	s := server.NewEventHorizonServer(pm, 8000)

	// 4. Handle OS Signals for graceful shutdown
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		sig := <-sigs
		log.Printf("[Main] Received signal %v. Initiating shutdown...", sig)
		
		// Stop the server
		// We'll trust the context cancellation and supervisor cleanup for the child processes
		pm.Stop()
		cancel()
		
		os.Exit(0)
	}()

	// 5. Start HTTP Server (Blocking)
	if err := s.Start(); err != nil {
		log.Fatalf("[Main] Failed to start HTTP server: %v", err)
	}
}
