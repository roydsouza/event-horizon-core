package server

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/roydsouza/event-horizon-core/internal/providers"
	"github.com/roydsouza/event-horizon-core/internal/supervisor"
)

type EventHorizonServer struct {
	supervisor *supervisor.ProcessManager
	openRouter *providers.OpenRouterClient
	port       int
	mux        *http.ServeMux
}

func NewEventHorizonServer(pm *supervisor.ProcessManager, port int) *EventHorizonServer {
	s := &EventHorizonServer{
		supervisor: pm,
		openRouter: providers.NewOpenRouterClient(),
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
		"status":     status,
		"port":       s.port,
		"engine":     "mlx_lm.server",
		"openrouter": s.openRouter.APIKey != "",
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

	// Routing Logic:
	// 1. If model is an alias (e.g. "best", "fast") OR explicitly remote (e.g. "anthropic/"), use OpenRouter (Tier 3)
	// 2. Otherwise, assume local MLX (Tier 1) and trigger hot-swap if mismatch.
	isRemote := false
	if _, ok := providers.Aliases[strings.ToLower(req.Model)]; ok {
		isRemote = true
	} else if strings.Contains(req.Model, "/") && !strings.HasPrefix(req.Model, "mlx-community/") {
		// Heuristic: model with "/" that isn't a community MLX model is likely remote (e.g. anthropic/claude)
		isRemote = true
	}

	if isRemote {
		log.Printf("[Server] Routing to OpenRouter: %s", req.Model)
		respBody, headers, statusCode, err := s.openRouter.ProxyRequest(r.Context(), body)
		if err != nil {
			log.Printf("[Server] OpenRouter error: %v", err)
			http.Error(w, fmt.Sprintf("OpenRouter Proxy Error: %v", err), http.StatusServiceUnavailable)
			return
		}
		defer respBody.Close()

		for k, v := range headers {
			w.Header()[k] = v
		}
		w.WriteHeader(statusCode)
		io.Copy(w, respBody)
		return
	}

	// Check if we need to hot-swap local MLX
	if req.Model != "" && req.Model != s.supervisor.CurrentModel() && req.Model != "default" {
		log.Printf("[Server] Client requested model %s, but %s is currently loaded. Initiating Hot-Swap...", req.Model, s.supervisor.CurrentModel())
		if err := s.supervisor.SwitchModel(r.Context(), req.Model); err != nil {
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
