package server

import (
	"bufio"
	"bytes"
	"context"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"sync"
	"sync/atomic"
	"time"

	"github.com/roydsouza/event-horizon-core/internal/supervisor"
)

// metricsTTL is how long a cached /metrics response is served before re-running
// the mlx.core subprocess. One subprocess spawn per 5s under continuous monitoring
// instead of one per request.
const metricsTTL = 5 * time.Second

// metricsCache is a simple TTL-bounded single-entry cache for /metrics responses.
type metricsCache struct {
	mu        sync.Mutex
	data      []byte
	fetchedAt time.Time
}

type AgentMetrics struct {
	mu            sync.Mutex
	RequestCount  int64   `json:"request_count"`
	TokensOut     int64   `json:"tokens_out"`
	TotalTTFT_Ms  int64   `json:"-"`
	AvgTTFT_Ms    int64   `json:"avg_ttft_ms"`
	TotalGen_Ms   int64   `json:"-"`
	AvgTPS        float64 `json:"avg_tps"`
	LastSeenNano  int64   `json:"last_seen_nano"`
}

type EventHorizonServer struct {
	supervisor *supervisor.ProcessManager
	port       int
	mux        *http.ServeMux
	ring       *EventRingBuffer

	agentMetrics sync.Map


	maintMu          sync.RWMutex
	maintenanceMode  bool
	maintenanceReqBy string
	maintenanceSince string

	// inFlightCount counts active HandleCompletions requests so HandleMaintenance
	// can drain them before declaring the server fully in maintenance mode.
	inFlightCount int64 // accessed via sync/atomic

	metrics metricsCache

	// Idle unloading (Phase 26). Both fields are Unix nanoseconds accessed atomically.
	// lastRequestNano: timestamp of the most recent HandleCompletions entry (0 = never).
	// idleSince: timestamp when the model was unloaded due to idle timeout (0 = not idle).
	lastRequestNano int64
	idleSince       int64
}

func NewEventHorizonServer(pm *supervisor.ProcessManager, port int, ring *EventRingBuffer) *EventHorizonServer {
	s := &EventHorizonServer{
		supervisor: pm,
		port:       port,
		mux:        http.NewServeMux(),
		ring:       ring,
	}

	s.mux.HandleFunc("/v1/chat/completions", s.HandleCompletions)
	s.mux.HandleFunc("/status", s.HandleStatus)

	s.mux.HandleFunc("/system/maintenance", s.adminAuthMiddleware(s.HandleMaintenance))
	s.mux.HandleFunc("/system/maintenance/release", s.adminAuthMiddleware(s.HandleMaintenanceRelease))
	s.mux.HandleFunc("/system/maintenance/status", s.adminAuthMiddleware(s.HandleMaintenanceStatus))
	s.mux.HandleFunc("/v1/model/swap", s.adminAuthMiddleware(s.HandleModelSwap))
	s.mux.HandleFunc("/metrics", s.adminAuthMiddleware(s.HandleMetrics))
	s.mux.HandleFunc("/metrics/agents", s.adminAuthMiddleware(s.HandleAgentMetrics))
	s.mux.HandleFunc("/system/memory", s.HandleMemory)
	s.mux.HandleFunc("/debug/events", s.adminAuthMiddleware(s.HandleDebugEvents))

	return s
}

func (s *EventHorizonServer) Start() error {
	addr := fmt.Sprintf(":%d", s.port)
	slog.Info("Event Horizon Daemon listening", "addr", addr)
	go s.pressureMonitor()
	go s.idleMonitor()
	return http.ListenAndServe(addr, s.mux)
}

// pressureMonitor logs transitions between memory pressure states every 30s.
// Operators can watch daemon.log for [WARN memory-pressure] lines without polling
// /system/memory. Only logs on state changes to avoid spamming the log.
func (s *EventHorizonServer) pressureMonitor() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()
	last := supervisor.PressureNormal
	for range ticker.C {
		stats, err := supervisor.GetMemoryStats()
		if err != nil {
			continue
		}
		if stats.Pressure == last {
			continue
		}
		switch stats.Pressure {
		case supervisor.PressureWarn:
			slog.Warn("memory-pressure elevated", "free_mb", stats.TotalFreeMB, "warn_threshold", 2048)
		case supervisor.PressureCritical:
			slog.Warn("memory-pressure critical", "free_mb", stats.TotalFreeMB, "critical_threshold", 1024)
		case supervisor.PressureNormal:
			slog.Info("memory-pressure normal", "free_mb", stats.TotalFreeMB)
		}
		last = stats.Pressure
	}
}

// idleMonitor unloads the MLX model after EHC_IDLE_TIMEOUT_SECONDS of inactivity,
// releasing ~4.6 GB of non-compressible Metal memory. Disabled when the env var is
// unset or 0. On the next request after an idle unload, HandleCompletions calls
// EnsureRunning to restart the model (cold-start penalty: 1.9–3.8s per E1 data).
func (s *EventHorizonServer) idleMonitor() {
	timeoutSec, err := strconv.ParseInt(os.Getenv("EHC_IDLE_TIMEOUT_SECONDS"), 10, 64)
	if err != nil || timeoutSec <= 0 {
		slog.Info("Idle unloading disabled")
		return
	}
	idleTimeout := time.Duration(timeoutSec) * time.Second
	slog.Info("Idle unloading enabled", "timeout", idleTimeout)

	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()
	for range ticker.C {
		last := atomic.LoadInt64(&s.lastRequestNano)
		if last == 0 {
			continue // no requests yet
		}
		if s.supervisor.GetStatus() != supervisor.StatusRunning {
			continue // already stopped or in a transition
		}
		if time.Since(time.Unix(0, last)) > idleTimeout {
			slog.Info("Model idle across timeout. Unloading.", "timeout", idleTimeout)
			if err := s.supervisor.IdleUnload(); err != nil {
				slog.Error("Idle unload failed", "error", err)
				continue
			}
			atomic.StoreInt64(&s.idleSince, time.Now().UnixNano())
			slog.Info("Model unloaded")
		}
	}
}

func (s *EventHorizonServer) HandleStatus(w http.ResponseWriter, r *http.Request) {
	status := s.supervisor.GetStatus()

	s.maintMu.RLock()
	mMode := s.maintenanceMode
	mReqBy := s.maintenanceReqBy
	mSince := s.maintenanceSince
	s.maintMu.RUnlock()

	var idleSinceStr interface{}
	if n := atomic.LoadInt64(&s.idleSince); n != 0 {
		idleSinceStr = time.Unix(0, n).UTC().Format(time.RFC3339)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":                   status,
		"port":                     s.port,
		"engine":                   "mlx_lm.server",
		"maintenance_mode":         mMode,
		"maintenance_requested_by": mReqBy,
		"maintenance_since":        mSince,
		"active_model":             s.supervisor.CurrentModel(),
		"idle_since":               idleSinceStr,
	})
}

func (s *EventHorizonServer) HandleCompletions(w http.ResponseWriter, r *http.Request) {
	s.maintMu.RLock()
	inMaintenance := s.maintenanceMode
	s.maintMu.RUnlock()

	b := make([]byte, 8)
	rand.Read(b)
	reqID := fmt.Sprintf("%x", b)
	w.Header().Set("X-Request-ID", reqID)

	agentName := r.Header.Get("X-Agent-Name")
	if agentName == "" {
		slog.Warn("missing X-Agent-Name", "remote_addr", r.RemoteAddr)
		agentName = "anonymous"
	}
	
	amItf, _ := s.agentMetrics.LoadOrStore(agentName, &AgentMetrics{})
	am := amItf.(*AgentMetrics)

	am.mu.Lock()
	am.RequestCount++
	am.LastSeenNano = time.Now().UnixNano()
	am.mu.Unlock()

	slog.Info("request", "agent", agentName, "request_id", reqID, "model", s.supervisor.CurrentModel())

	adminToken := r.Header.Get("X-EHC-Admin-Token")
	expectedToken := os.Getenv("EHC_ADMIN_TOKEN")
	isAdmin := expectedToken != "" && adminToken == expectedToken

	if inMaintenance && !isAdmin {
		w.Header().Set("Retry-After", "60")
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusServiceUnavailable)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error":       "EHC is in maintenance mode",
			"retry_after": 60,
		})
		return
	}

	// Record for idle timeout tracking.
	atomic.StoreInt64(&s.lastRequestNano, time.Now().UnixNano())

	// If model was unloaded by idle timeout, restart it before serving.
	if s.supervisor.GetStatus() == supervisor.StatusStopped {
		slog.Info("Model was idle-unloaded. Restarting for incoming request")
		if err := s.supervisor.EnsureRunning(context.Background()); err != nil {
			http.Error(w, fmt.Sprintf("Failed to restart idle model: %v", err), http.StatusServiceUnavailable)
			return
		}
		atomic.StoreInt64(&s.idleSince, 0)
	}

	// Count this request as in-flight so HandleMaintenance can drain properly.
	// Decrement happens on function return via defer.
	atomic.AddInt64(&s.inFlightCount, 1)
	defer atomic.AddInt64(&s.inFlightCount, -1)

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

	// Trigger hot-swap if the client requested a different model.
	// context.Background() is intentional — a client disconnect must not cancel
	// a swap mid-flight, which would leave mlx_lm.server in an inconsistent state.
	if req.Model != "" && req.Model != s.supervisor.CurrentModel() && req.Model != "default" {
		slog.Info("Hot-Swap Initiated", "requested_model", req.Model, "current_model", s.supervisor.CurrentModel())
		if err := s.supervisor.SwitchModel(context.Background(), req.Model); err != nil {
			slog.Error("Hot-Swap Failed", "error", err, "model", req.Model)
			http.Error(w, fmt.Sprintf("Failed to load model %s: %v", req.Model, err), http.StatusInternalServerError)
			return
		}
	}

	// Proxy to supervised MLX server (port 8080).
	targetURL := "http://127.0.0.1:8080/v1/chat/completions"
	proxyReq, err := http.NewRequestWithContext(r.Context(), http.MethodPost, targetURL, bytes.NewBuffer(body))
	if err != nil {
		http.Error(w, "Error creating proxy request", http.StatusInternalServerError)
		return
	}
	for k, v := range r.Header {
		proxyReq.Header[k] = v
	}

	// Firewall hook stub (Phase 24)
	if fwBase := os.Getenv("EHC_AGENT_FIREWALL_ENDPOINT"); fwBase != "" {
		fwURL := fmt.Sprintf("%s/v1/firewall/check", fwBase)
		fwReq, _ := http.NewRequest(http.MethodPost, fwURL, bytes.NewReader([]byte(fmt.Sprintf(`{"agent":"%s"}`, agentName))))
		fwReq.Header.Set("Content-Type", "application/json")
		
		fwClient := &http.Client{Timeout: 100 * time.Millisecond}
		fwResp, fwErr := fwClient.Do(fwReq)
		if fwErr != nil {
			slog.Warn("firewall hook failed (fail-open)", "agent", agentName, "error", fwErr)
		} else {
			fwResp.Body.Close()
			if fwResp.StatusCode >= 400 {
				slog.Warn("firewall hook rejected request", "agent", agentName, "status", fwResp.StatusCode)
				// Fail-open for now. Strict mode will block later.
			}
		}
	}

	proxyStart := time.Now()
	client := &http.Client{Timeout: 300 * time.Second}
	resp, err := client.Do(proxyReq)
	if err != nil {
		slog.Error("Proxy error to MLX", "error", err)
		http.Error(w, "Error connecting to MLX backend. Is the server running?", http.StatusServiceUnavailable)
		return
	}
	defer resp.Body.Close()

	for k, v := range resp.Header {
		w.Header()[k] = v
	}
	w.WriteHeader(resp.StatusCode)

	// SSE-aware proxy: flush after each newline so streaming tokens reach the client
	// incrementally rather than arriving in 32KB batches. ReadBytes('\n') returns each
	// SSE line (including the terminating \n) as a single chunk; the Flusher ensures it
	// is written to the wire immediately. For non-streaming responses the entire body
	// arrives as one chunk and is written in a single pass — behaviour is unchanged.
	flusher, canFlush := w.(http.Flusher)
	reader := bufio.NewReaderSize(resp.Body, 4096)
	
	firstChunk := true
	var chunkCount int64

	for {
		chunk, readErr := reader.ReadBytes('\n')
		if len(chunk) > 0 {
			if firstChunk {
				ttft := time.Since(proxyStart).Milliseconds()
				am.mu.Lock()
				am.TotalTTFT_Ms += ttft
				if am.RequestCount > 0 {
					am.AvgTTFT_Ms = am.TotalTTFT_Ms / am.RequestCount
				}
				am.LastSeenNano = time.Now().UnixNano()
				am.mu.Unlock()
				firstChunk = false
			}

			w.Write(chunk)
			if canFlush {
				flusher.Flush()
			}

			// Count chunks starting with "data: " as ~tokens
			if bytes.HasPrefix(chunk, []byte("data: ")) && !bytes.Contains(chunk, []byte("[DONE]")) {
				chunkCount++
			}
		}
		if readErr != nil {
			break
		}
	}

	// Update token counts
	genDurationMs := time.Since(proxyStart).Milliseconds()
	
	if chunkCount > 0 {
		am.mu.Lock()
		am.TokensOut += chunkCount
		am.TotalGen_Ms += genDurationMs
		if am.TotalGen_Ms > 0 {
			am.AvgTPS = float64(am.TokensOut) / (float64(am.TotalGen_Ms) / 1000.0)
		}
		am.mu.Unlock()
	} else if !firstChunk {
		am.mu.Lock()
		am.TokensOut += 1 // Generic default for non-streamed full responses
		am.TotalGen_Ms += genDurationMs
		if am.TotalGen_Ms > 0 {
			am.AvgTPS = float64(am.TokensOut) / (float64(am.TotalGen_Ms) / 1000.0)
		}
		am.mu.Unlock()
	}
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

	// Drain: wait up to 10s for in-flight inference requests to complete.
	// maintenanceMode is already true above, so new requests get 503 immediately.
	// We poll inFlightCount until it reaches zero or the deadline expires.
	drainDeadline := time.Now().Add(10 * time.Second)
	for time.Now().Before(drainDeadline) {
		if atomic.LoadInt64(&s.inFlightCount) == 0 {
			break
		}
		time.Sleep(100 * time.Millisecond)
	}
	if remaining := atomic.LoadInt64(&s.inFlightCount); remaining > 0 {
		slog.Warn("Maintenance drain timeout", "remaining_in_flight", remaining)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":       "maintenance",
		"active_model": s.supervisor.CurrentModel(),
		"since":        sSince,
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
		slog.Info("Hot-Swapping Model (Promote)", "to", req.PromoteModel)
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
		"status":       "operational",
		"active_model": s.supervisor.CurrentModel(),
		"promoted":     promoted,
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
		"requested_by":   reqBy,
		"since":          since,
		"active_model":   s.supervisor.CurrentModel(),
	})
}

// HandleModelSwap handles explicit POST /v1/model/swap requests.
// Returns HTTP 409 immediately if a swap is already in progress rather than
// blocking for the full swap duration (20-30s). Clients should retry after
// polling /system/maintenance/status.
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
			"status":       "success",
			"active_model": current,
		})
		return
	}

	slog.Info("Explicit model swap", "from", current, "to", req.Model)
	if err := s.supervisor.TrySwitchModel(context.Background(), req.Model); err != nil {
		if err == supervisor.ErrSwapInProgress {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusConflict)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"error": "model swap already in progress — poll /system/maintenance/status and retry",
			})
			return
		}
		slog.Error("Explicit swap failed", "error", err)
		http.Error(w, fmt.Sprintf("Failed to load model %s: %v", req.Model, err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":       "success",
		"active_model": req.Model,
	})
}

// HandleMetrics returns MLX Metal memory statistics.
// Responses are cached for metricsTTL (5s) to avoid spawning a Python subprocess
// on every monitoring poll.
func (s *EventHorizonServer) HandleMetrics(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	// Serve from cache if fresh.
	s.metrics.mu.Lock()
	if len(s.metrics.data) > 0 && time.Since(s.metrics.fetchedAt) < metricsTTL {
		cached := make([]byte, len(s.metrics.data))
		copy(cached, s.metrics.data)
		s.metrics.mu.Unlock()
		w.Header().Set("Content-Type", "application/json")
		w.Write(cached)
		return
	}
	s.metrics.mu.Unlock()

	// Cache miss — spawn the subprocess.
	cmdStr := "import mlx.core; import json; print(json.dumps({'active_mb': mlx.core.metal.get_active_memory()//1024//1024, 'peak_mb': mlx.core.metal.get_peak_memory()//1024//1024}))"
	out, err := exec.Command("uv", "run", "python", "-c", cmdStr).Output()
	if err != nil {
		slog.Error("Metrics error", "error", err)
		http.Error(w, "Failed to fetch metrics", http.StatusInternalServerError)
		return
	}

	s.metrics.mu.Lock()
	s.metrics.data = out
	s.metrics.fetchedAt = time.Now()
	s.metrics.mu.Unlock()

	w.Header().Set("Content-Type", "application/json")
	w.Write(out)
}

func (s *EventHorizonServer) HandleMemory(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}

	stats, err := supervisor.GetMemoryStats()
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to fetch memory stats: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

func (s *EventHorizonServer) HandleDebugEvents(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	if s.ring == nil {
		w.Write([]byte("[]"))
		return
	}
	events := s.ring.GetEvents()
	json.NewEncoder(w).Encode(events)
}

func (s *EventHorizonServer) HandleAgentMetrics(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}
	
	metrics := make(map[string]AgentMetrics)
	s.agentMetrics.Range(func(key, value any) bool {
		agentName := key.(string)
		am := value.(*AgentMetrics)
		am.mu.Lock()
		metrics[agentName] = *am
		am.mu.Unlock()
		return true
	})

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(metrics)
}
