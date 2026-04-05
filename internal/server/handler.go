package server

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/roydsouza/event-horizon-core/internal/supervisor"
)

type EventHorizonServer struct {
	supervisor *supervisor.ProcessManager
	port       int
	mux        *http.ServeMux
}

func NewEventHorizonServer(pm *supervisor.ProcessManager, port int) *EventHorizonServer {
	s := &EventHorizonServer{
		supervisor: pm,
		port:       port,
		mux:        http.NewServeMux(),
	}

	s.mux.HandleFunc("/v1/chat/completions", s.HandleCompletions)
	s.mux.HandleFunc("/status", s.HandleStatus)

	return s
}

func (s *EventHorizonServer) Start() error {
	addr := fmt.Sprintf(":%d", s.port)
	log.Printf("[Server] Event Horizon Daemon listening on %s", addr)
	return http.ListenAndServe(addr, s.mux)
}

func (s *EventHorizonServer) HandleStatus(w http.ResponseWriter, r *http.Request) {
	status := s.supervisor.GetStatus()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": status,
		"port":   s.port,
		"engine": "mlx_lm.server",
	})
}

func (s *EventHorizonServer) HandleCompletions(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Error reading request body", http.StatusInternalServerError)
		return
	}

	// Extract requested model
	var req struct {
		Model string `json:"model"`
	}
	json.Unmarshal(body, &req)

	// Routing Logic: Assume local MLX (Tier 1) and trigger hot-swap if mismatch.

	// Check if we need to hot-swap local MLX.
	// Use context.Background() so the swap is not cancelled if the HTTP client
	// disconnects or times out mid-load — a cancelled swap leaves mlx_lm.server dead.
	if req.Model != "" && req.Model != s.supervisor.CurrentModel() && req.Model != "default" {
		log.Printf("[Server] Client requested model %s, but %s is currently loaded. Initiating Hot-Swap...", req.Model, s.supervisor.CurrentModel())
		if err := s.supervisor.SwitchModel(context.Background(), req.Model); err != nil {
			log.Printf("[Server] Hot-Swap Failed: %v", err)
			http.Error(w, fmt.Sprintf("Failed to load model %s: %v", req.Model, err), http.StatusInternalServerError)
			return
		}
	}

	// Local Proxy to Supervised MLX Server (Port 8080)
	targetURL := "http://127.0.0.1:8080/v1/chat/completions"
	proxyReq, err := http.NewRequestWithContext(r.Context(), http.MethodPost, targetURL, bytes.NewBuffer(body))
	if err != nil {
		http.Error(w, "Error creating proxy request", http.StatusInternalServerError)
		return
	}

	for k, v := range r.Header {
		proxyReq.Header[k] = v
	}

	client := &http.Client{Timeout: 300 * time.Second}
	resp, err := client.Do(proxyReq)
	if err != nil {
		log.Printf("[Server] Proxy error to MLX: %v", err)
		http.Error(w, "Error connecting to MLX backend. Is the server running?", http.StatusServiceUnavailable)
		return
	}
	defer resp.Body.Close()

	for k, v := range resp.Header {
		w.Header()[k] = v
	}
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}
