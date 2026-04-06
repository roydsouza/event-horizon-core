# EHC Solution Architectures

> **Purpose:** Volatile, open-ended research catalog. Records all proposed, prototyped, 
> and historical technical designs for Event Horizon Core and its neighbors. 
> This is a living document for brainstorming and deep-diving into individual 
> candidate architectures.
>
> **Cross-references:** [LIMITATIONS.md](LIMITATIONS.md) (diagnosis) · [ROADMAP.md](ROADMAP.md) (selection) · [TASKS.md](TASKS.md) (execution)

---

## 🏗️ Core Orchestration Backends

### S1: MLX-Swift Native Inference Library `[PROPOSED — GATED]`
*Proposed to solve: L1 (Cold-Start Latency), L6 (Python Dependency)*

| Property | Details |
|:---|:---|
| **Concept** | Re-implement the inference core as a Swift library/binary using the Apple MLX-Swift bindings. Go keeps orchestration; Swift does inference via Unix socket or in-process FFI. |
| **Pros** | Eliminates 2-4s of Python/uv startup overhead; enables in-process model management (no SIGKILL cycle); potential for thread-level multi-model residency with shared Metal device. |
| **Cons** | **Ecosystem immature as of April 2026**: MLX-Swift lacks production-serving features present in `mlx_lm.server` — no HTTP server, no continuous batching, no prefix caching, no SSE streaming, limited LoRA support. Reimplementing these is 2-4 months of work. The dominant cold-start cost is weight loading (language-independent), so gains may be modest. |
| **Architectural fit** | Good *long-term*: Swift is Apple's direction for native Metal work. Poor *near-term*: `mlx_lm.server` has years of inference-serving investment that MLX-Swift doesn't replicate yet. |
| **Recommendation** | Desirable end-state, not a near-term priority. Gate behind Experiment E1 (cold-start measurement) and a 48-hour spike (E3). Do not commit full engineering resources without empirical evidence of >30% startup overhead. |
| **Decision gate** | E1 shows Python overhead >30% of swap time AND E3 spike TTFT <2s → greenlight Phase 16. Otherwise: pursue S4 (LoRA) or S3 (mmap) instead. |
| **Alternatives** | S2 (Dual-Process Python), S3 (mmap Weights), S4 (LoRA multi-tenancy). |
| **Experiment Link** | [E3 (48-Hour Spike)](LIMITATIONS.md#e3-mlx-swift-48-hour-spike) |

**MLX-Swift ecosystem checklist (verify before committing to Phase 16):**
- [ ] Prefix caching (critical for multi-turn agent conversations — currently `--prompt-cache-size 2048`)
- [ ] SSE streaming (required for OpenFang and real-time UX)
- [ ] LoRA adapter loading (required for S4 multi-tenancy strategy)
- [ ] 4-bit/8-bit quantization parity with mlx-lm
- [ ] HTTP server (or determine if Go→Swift IPC via Unix socket is workable)

---

### S2: Dual-Process Python Pre-warming `[PROPOSED — CONTINGENCY]`
*Proposed to solve: L1 (Cold-Start Latency)*

| Property | Details |
|:---|:---|
| **Concept** | Launch a second `mlx_lm.server` in the background on a new port; cut over once healthy. |
| **Pros** | Zero-downtime swaps with zero new language dependencies. Works today. |
| **Cons** | Double VRAM pressure during warm-up; complex state management in the Go supervisor. Cannot be used for models larger than ~10GB total on M5 24GB. |
| **Status** | Pursue only if E3 (Swift spike) fails or is deferred and LoRA multi-tenancy (S4) doesn't provide sufficient model diversity. |
| **Phase** | TASKS Phase 21 |

---

### S3: Memory-Mapped Weight Persistence `[RESEARCHING]`
*Proposed to solve: L1 (Cold-Start Latency)*

| Property | Details |
|:---|:---|
| **Concept** | Keep weights in a resident shared memory block (shm) or `mmap`'d file so new processes can "attach" to them instantly. |
| **Pros** | ~1s restart time without language migration. Addresses the dominant bottleneck directly. |
| **Cons** | Depends on `mlx-lm` supporting shared weight buffers; complex on macOS unified memory. |
| **Investigation needed** | Does `mlx.core.load()` support mmap mode for safetensors? Can we pin the Metal buffer across process restarts? |

---

## 🧠 Multi-Tenancy & Memory Strategies

### S4: LoRA-Based Multi-Tenancy `[PROPOSED — HIGH PRIORITY]`
*Proposed to solve: L2 (Single-Model Residency), L1 (Cold-Start via adapter swap)*

| Property | Details |
|:---|:---|
| **Concept** | Standardize on a single base model (e.g., Hermes-3-8B) and swap low-rank adapters (<200MB) for different tasks. The base model stays resident; only the LoRA head changes. |
| **Pros** | No model unloading; <1s adapter switching; multiple "agents" share 95% of VRAM. Full fleet example: 4.2GB base + 4×100MB adapters = 4.6GB total, leaving 19GB for KV caches. Works today with `mlx-lm` LoRA support. |
| **Cons** | Requires training task-specific LoRAs (weeks of `llm-factory` work); potential quality gap vs. purpose-built models. |
| **Why this matters** | If LoRA multi-tenancy works, it makes S1 (Swift migration) *less urgent* — you get sub-second "model switching" without changing the language layer at all. This is the highest-leverage near-term exploration. |
| **Experiment Link** | [E2 (LoRA Pilot)](LIMITATIONS.md#e2-lora-multi-tenancy-pilot) |
| **Phase** | No dedicated phase yet — depends on `llm-factory` Phase 2 |

---

### S5: Metal Heap (`MTLHeap`) Virtualization `[REJECTED]`
*Proposed to solve: L5 (VRAM Fragmentation)*

| Property | Details |
|:---|:---|
| **Concept** | Manually manage Metal allocation heaps to pack multiple models into non-continuous VRAM. |
| **Pros** | Optimal physical memory utilization. |
| **Cons** | Obsoleted by MLX's internal allocator improvements; extremely brittle and maintenance-heavy. |
| **Decision ADR** | Rejected 2026-04-06: High complexity, low perceived ROI vs. S4. |

---

## 📊 Observability & Maintenance

### S6: Subprocess Metrics Caching `[IMPLEMENTED — 2026-04-06]`
*Solved: L3 (Metrics Overhead)*

| Property | Details |
|:---|:---|
| **Concept** | TTL cache (5s) in `handler.go` around the `uv run python` metrics call. Cache miss spawns subprocess; cache hit serves from memory. |
| **Implementation** | `metricsCache` struct with `sync.Mutex`, `[]byte data`, `time.Time fetchedAt`. `metricsTTL = 5 * time.Second`. |
| **Result** | One subprocess spawn per 5s under continuous monitoring instead of one per request. |
| **Remaining gap** | Python dependency for this metric still exists. Future: read from `ioreg`/`sysctl` in Go directly, or upstream `mlx_lm.server` exposes a `/metrics` endpoint. |

---

### S7: SSE-Aware Line-Buffered Proxy `[IMPLEMENTED — 2026-04-06]`
*Solved: L4 (Streaming Proxy Buffering)*

| Property | Details |
|:---|:---|
| **Concept** | Replace `io.Copy` with `bufio.ReadBytes('\n')` loop + `http.Flusher.Flush()` after each SSE event line. |
| **Implementation** | `flusher, canFlush := w.(http.Flusher)` — graceful fallback if ResponseWriter doesn't implement Flusher. Non-streaming responses unaffected (arrive as one chunk, written in single pass). |
| **Result** | OpenFang and any streaming-mode client now receive tokens incrementally as generated. TTFT reflects actual first-token time. |

---

### S8: In-Flight Drain for Maintenance Mode `[IMPLEMENTED — 2026-04-06]`
*Solved: L8 (Maintenance Drain Race)*

| Property | Details |
|:---|:---|
| **Concept** | `inFlightCount int64` atomic counter on `EventHorizonServer`. `HandleCompletions` increments/decrements via `defer`. `HandleMaintenance` polls until zero with 10s deadline. |
| **Implementation** | `sync/atomic.AddInt64` / `LoadInt64`. Drain loop: 100ms tick, 10s timeout, log warning if requests still in-flight at deadline. |
| **Residual race** | Sub-millisecond window between maintenance check and counter increment. Accepted — operator-initiated maintenance is not high-frequency. |

---

### S9: Non-Blocking Model Swap (409 on Contention) `[IMPLEMENTED — 2026-04-06]`
*Solved: L9 (ModelSwap blocks on in-progress swaps)*

| Property | Details |
|:---|:---|
| **Concept** | `TrySwitchModel()` in `ProcessManager` uses `swapMu.TryLock()` (Go 1.18+). Returns `ErrSwapInProgress` immediately if lock is held. `HandleModelSwap` maps this to HTTP 409 with retry guidance. |
| **Implementation** | `doSwitch()` extracted as shared body; `SwitchModel()` uses blocking `Lock()`, `TrySwitchModel()` uses `TryLock()`. `HandleCompletions` implicit swaps still use blocking path (correct — those requests should queue). |

---

## 🔗 Cross-Project Solutions (Dependency Oriented)

### S10: `llm-proving-ground` Automated Regression `[PROPOSED]`
*Oriented toward: llm-proving-ground*

| Property | Details |
|:---|:---|
| **Concept** | Proving ground uses EHC's Maintenance API to automatically test new backend solutions (like S1) against production SLOs before cutover. |
| **Benefit** | Proactive validation of architectural changes. Phase 18 now live — proving ground EHC client stubs can be replaced with real calls. |

---

### S11: `llm-factory` LoRA Pipeline Integration `[PROPOSED]`
*Oriented toward: llm-factory*

| Property | Details |
|:---|:---|
| **Concept** | Factory exports specialized adapters specifically for EHC's S4 Multi-Tenancy strategy. |
| **Benefit** | Creates a closed-loop tuning feedback system. Depends on llm-factory Phase 2 (EHC integration) being built. |

---

## 📝 Archives & Histograph

> *Design decisions and retired solutions.*

| Date | ID | Status | Note |
|:---|:---|:---|:---|
| 2026-04-06 | S6 | `[IMPLEMENTED]` | Metrics TTL cache — eliminates subprocess churn under monitoring. |
| 2026-04-06 | S7 | `[IMPLEMENTED]` | SSE-aware proxy — fixes OpenFang streaming TTFT. |
| 2026-04-06 | S8 | `[IMPLEMENTED]` | In-flight drain — maintenance mode now actually drains requests. |
| 2026-04-06 | S9 | `[IMPLEMENTED]` | TrySwitchModel — /v1/model/swap returns 409 on contention. |
| 2026-04-06 | S5 | `[REJECTED]` | MTLHeap virtualization — high complexity, low ROI vs. LoRA. |
| 2026-04-01 | S12 | `[RETIRED]` | Removed Ollama/Llama.cpp providers to focus on MLX performance. |
| 2026-03-31 | S13 | `[RETIRED]` | Python-only orchestrator (replaced by Go daemon). |
