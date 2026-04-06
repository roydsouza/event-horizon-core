package server

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"sync"
	"time"

	"github.com/roydsouza/event-horizon-core/internal/supervisor"
)

type EventHorizonServer struct {
	supervisor *supervisor.ProcessManager
	port       int
	mux        *http.ServeMux

	maintMu          sync.RWMutex
	maintenanceMode  bool
	maintenanceReqBy string
	maintenanceSince string
}

func NewEventHorizonServer(pm *supervisor.ProcessManager, port int) *EventHorizonServer {
	s := &EventHorizonServer{
		supervisor: pm,
		port:       port,
		mux:        http.NewServeMux(),
	}

	s.mux.HandleFunc("/v1/chat/completions", s.HandleCompletions)
	s.mux.HandleFunc("/status", s.HandleStatus)
	
	s.mux.HandleFunc("/system/maintenance", s.adminAuthMiddleware(s.HandleMaintenance))
	s.mux.HandleFunc("/system/maintenance/release", s.adminAuthMiddleware(s.HandleMaintenanceRelease))
	s.mux.HandleFunc("/system/maintenance/status", s.adminAuthMiddleware(s.HandleMaintenanceStatus))
	s.mux.HandleFunc("/v1/model/swap", s.adminAuthMiddleware(s.HandleModelSwap))
	s.mux.HandleFunc("/metrics", s.adminAuthMiddleware(s.HandleMetrics))

	return s
}

func (s *EventHorizonServer) Start() error {
	addr := fmt.Sprintf(":%d", s.port)
	log.Printf("[Server] Event Horizon Daemon listening on %s", addr)
	return http.ListenAndServe(addr, s.mux)
}

func (s *EventHorizonServer) HandleStatus(w http.ResponseWriter, r *http.Request) {
	status := s.supervisor.GetStatus()
	
	s.maintMu.RLock()
	mMode := s.maintenanceMode
	mReqBy := s.maintenanceReqBy
	mSince := s.maintenanceSince
	s.maintMu.RUnlock()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": status,
		"port":   s.port,
		"engine": "mlx_lm.server",
		"maintenance_mode": mMode,
		"maintenance_requested_by": mReqBy,
		"maintenance_since": mSince,
		"active_model": s.supervisor.CurrentModel(),
	})
}

func (s *EventHorizonServer) HandleCompletions(w http.ResponseWriter, r *http.Request) {
	s.maintMu.RLock()
	inMaintenance := s.maintenanceMode
	s.maintMu.RUnlock()

	if inMaintenance {
		w.Header().Set("Retry-After", "60")
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error": "EHC is in maintenance mode",
			"retry_after": 60,
		})
		return
	}

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

func (s *EventHorizonServer) adminAuthMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		token := r.Header.Get("X-EHC-Admin-Token")
		expected := os.Getenv("EHC_ADMIN_TOKEN")
		if expected == "" || token != expected {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}
		next(w, r)
	}
}

func (s *EventHorizonServer) HandleMaintenance(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Reason      string `json:"reason"`
		RequestedBy string `json:"requested_by"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Error parsing request body", http.StatusBadRequest)
		return
	}

	s.maintMu.Lock()
	if s.maintenanceMode {
		s.maintMu.Unlock()
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusConflict)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error": "already in maintenance mode",
		})
		return
	}
	s.maintenanceMode = true
	s.maintenanceReqBy = req.RequestedBy
	s.maintenanceSince = time.Now().UTC().Format(time.RFC3339)
	sSince := s.maintenanceSince
	s.maintMu.Unlock()

	// Drain in-flight requests gracefully
	time.Sleep(5 * time.Second)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "maintenance",
		"active_model": s.supervisor.CurrentModel(),
		"since": sSince,
	})
}

func (s *EventHorizonServer) HandleMaintenanceRelease(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		PromoteModel string `json:"promote_model"`
	}
	json.NewDecoder(r.Body).Decode(&req)

	promoted := false
	if req.PromoteModel != "" && req.PromoteModel != s.supervisor.CurrentModel() {
		log.Printf("[Server] Hot-Swapping Model (Promote): -> %s", req.PromoteModel)
		if err := s.supervisor.SwitchModel(context.Background(), req.PromoteModel); err != nil {
			http.Error(w, fmt.Sprintf("Failed to swap to promote_model %s: %v", req.PromoteModel, err), http.StatusInternalServerError)
			return
		}
		promoted = true
	}

	s.maintMu.Lock()
	s.maintenanceMode = false
	s.maintenanceReqBy = ""
	s.maintenanceSince = ""
	s.maintMu.Unlock()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "operational",
		"active_model": s.supervisor.CurrentModel(),
		"promoted": promoted,
	})
}

func (s *EventHorizonServer) HandleMaintenanceStatus(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	s.maintMu.RLock()
	mMode := s.maintenanceMode
	reqBy := s.maintenanceReqBy
	since := s.maintenanceSince
	s.maintMu.RUnlock()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"in_maintenance": mMode,
		"requested_by": reqBy,
		"since": since,
		"active_model": s.supervisor.CurrentModel(),
	})
}

func (s *EventHorizonServer) HandleModelSwap(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Model string `json:"model"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Error parsing request", http.StatusBadRequest)
		return
	}
	
	if req.Model == "" {
		http.Error(w, "Model field is required", http.StatusBadRequest)
		return
	}
	
	current := s.supervisor.CurrentModel()
	if req.Model == current {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status": "success",
			"active_model": current,
		})
		return
	}
	
	log.Printf("[Server] Explicit model swap: %s -> %s", current, req.Model)
	if err := s.supervisor.SwitchModel(context.Background(), req.Model); err != nil {
		log.Printf("[Server] Hot-Swap Failed: %v", err)
		http.Error(w, fmt.Sprintf("Failed to load model %s: %v", req.Model, err), http.StatusInternalServerError)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "success",
		"active_model": req.Model,
	})
}

func (s *EventHorizonServer) HandleMetrics(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	cmdStr := "import mlx.core; import json; print(json.dumps({'active_mb': mlx.core.metal.get_active_memory()//1024//1024, 'peak_mb': mlx.core.metal.get_peak_memory()//1024//1024}))"
	out, err := exec.Command("uv", "run", "python", "-c", cmdStr).Output()
	if err != nil {
		log.Printf("[Server] Metrics error: %v", err)
		http.Error(w, "Failed to fetch metrics", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(out)
}
