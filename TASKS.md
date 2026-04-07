# Event Horizon Core: Tasks

> **Cross-references:** [LIMITATIONS.md](LIMITATIONS.md) (why) · [ROADMAP.md](ROADMAP.md) (where) · [REVIEW_04_06.md](REVIEW_04_06.md) (discussion)

## 🔁 Recurring Tasks

> **Opening ritual for both agents**: On every session open, check the table below.
> If `Next Due` ≤ today, surface the item to the operator before starting other work.
> After completing a recurring task, update `Next Due` by adding the interval to today's date.

| Frequency | Next Due | Task | Notes |
|:----------|:---------|:-----|:------|
| Weekly | 2026-04-12 | **Model cache audit** — review `~/.cache/huggingface/hub/`, decide what to keep/remove. Cross-check with `llm-proving-ground/reports/cache-manifest.md` for evaluation downloads. | See "Model Cache Inventory" section below for current state |
| Weekly | 2026-04-12 | **Gemma 4 26B A4B readiness check** — is `mlx-lm >= 0.32.x` on PyPI? Is PR #1112 closed? | `uv run python3 -c "from mlx_lm.models import gemma4; print('ready')"` and check https://github.com/ml-explore/mlx-lm/pull/1112 |

---

## Completed Phases (Archive)

<details>
<summary>Click to expand Phases 1–12 (all completed)</summary>

| Phase | Title | Status | Key Outcome |
|:------|:------|:-------|:------------|
| 1 | Environment & Setup | ✅ | OpenRouter activation, `uv` transition |
| 2 | Performance & Connectivity | ✅ | VRAM guard (24GB), CLI help, agent setup guides |
| 3 | Concurrency Torture Testing | ✅ | MLX stable at 2 concurrent; Ollama 60s timeout identified |
| 4 | Orchestration & Resource Optimization | ✅ | Pivoted to `mlx_lm.server` as primary substrate |
| 5 | Native Architecture Integration | ✅ | `RemoteNativeProvider` wrapping `mlx_lm.server` |
| 6 | Substrate Streamlining (MLX-Only) | ✅ | Removed Llama.cpp and Ollama backends |
| 7 | Go Substrate Migration | ✅ | Zero-dependency Go daemon on port 8000 |
| 8 | Acceptance Criteria & Test Plan | ✅ | 50+ concurrent stress tests; zombie recovery verified |
| 9 | Python Eradication | ✅ | Deleted orchestrator.py, providers/, pruned deps |
| 10 | Local-Only Simplification | ✅ | Removed OpenRouter; local-only architecture |
| 11 | Hardware Performance & SLO Verification | ✅ | 0.74s P95 TTFT; SLOs documented |
| 12 | LLM Candidate Evaluation | ✅ | Hermes-3-8B-4bit selected as Apex Archetype |

> **Phase 12 Key Finding:** On 24GB M5, multi-agent workloads are strictly limited to the 8B parameter tier. Hermes-3-Llama-3.1-8B-4bit is the only tested model maintaining double-digit TPS under 5-client pressure.

</details>

## Phase 13: Gemma 4 Native Integration & Evaluation [ON HOLD]
> **Status**: Reverted to Phase 12-stable substrate on 2026-04-03 due to lack of official `mlx-lm` architecture support for native multimodal Gemma 4.0.
- [ ] **Research MLX Compatibility**:
    - [x] Confirmed `mlx-lm 0.31.2` git main lacks `gemma4` architecture implementation.
- [ ] **Download Gemma 4 Modules**: [ABORTED]
    - [ ] `mlx-community/gemma-4-e4b-it-4bit`
    - [ ] `mlx-community/gemma-4-26b-a4b-it-4bit`
- [x] **Post-Gemma Rollback**:
    - [x] Reinstalled stable `mlx-lm==0.31.1`.
    - [x] Reverted `tests/benchmark_candidates.py` to Phase 12 baseline.
    - [x] Rebuilt Go binary to fix stale `/status` reporting (verified `engine: mlx_lm.server`).
- [ ] **Single-Client Benchmarking**:
    - [ ] Measure TTFT and TPS for E4B (Claw/Agent profile).
    - [ ] Measure TTFT and TPS for 26B MoE (PDP/Firewall profile).
- [ ] **Stability & Memory Profiling**:
    - [ ] Observe VRAM idle vs load for both modules on 25GB M5.
- [ ] **Substrate Integration**:
    - [ ] Rebuild Go binary to fix stale `/status` and verify swapping for new modules.


## Phase 15: Concurrency Correctness & Multiplexing Research [IN PROGRESS]

> **Context**: Independent architecture review (2026-04-04) identified a hot-swap race
> condition and open questions about the mlx_lm.server backend's correctness under
> concurrent load. Phase 15 resolves the immediate correctness issue and captures
> the decision space for a potential backend change.

- [x] **Fix hot-swap race condition in ProcessManager** (commit 9ad2cbf):
    - Added `swapMu sync.Mutex` to serialize `SwitchModel()` — only one swap runs at a time
    - Added `mu sync.RWMutex` to protect `modelPath` and `status` field reads/writes from
      all goroutines (HTTP handler goroutines, background `cmd.Wait()` reaper)
    - `SwitchModel` re-checks model inside the lock — redundant swaps skip with a log line
    - `CurrentModel()` and `GetStatus()` now hold `mu.RLock()` for safe concurrent reads
- [x] **Document MLX multiplexing alternatives** (`docs/research/MLX_MULTIPLEXING_OPTIONS.md`):
    - Captures: vllm-mlx, mlx_lm upstream bug status, multi-instance pool, vLLM sleep mode, aLoRA
    - Flags known mlx_lm.server concurrency bugs (KV contamination #965, kernel panic #883)
    - Includes open research questions and a preliminary recommendation order
- [ ] **Verify upstream mlx_lm bug status**: Check if #965, #754, #883 are fixed in the
    current pinned version. If fixed, no backend change needed. Run: `uv run python -m mlx_lm --version`
    or `uv pip show mlx-lm` and check the changelog against the issue numbers.
- [ ] **Operator reviews** `docs/research/MLX_MULTIPLEXING_OPTIONS.md` and decides direction
- [ ] **Implement chosen direction** (TBD — see research doc)

## Phase 16: MLX-Swift & Native Migration [GATED — DO NOT START WITHOUT E1 + E3]

> **Goal**: Eradicate the Python dependency and `uv` execution overhead.
>
> **Gate**: This phase must not start until Experiment E1 (cold-start breakdown) shows
> Python/uv overhead >30% of total swap time AND Experiment E3 (48h spike) shows
> Swift TTFT <2s. See [ROADMAP R4](ROADMAP.md#r4-mlx-swift-spike-48-hours--after-r2) and
> [LIMITATIONS E3](LIMITATIONS.md#e3-mlx-swift-48-hour-spike) for full rationale.
>
> **Architectural note**: Target architecture if greenlit is Go Orchestrator → Unix Socket →
> Swift Inference Library. NOT a full Swift-NIO rewrite — Go keeps orchestration.

- [ ] **Pre-conditions (must complete first)**:
    - [ ] E1: Instrument `manager.go` and measure actual cold-start breakdown (see LIMITATIONS.md)
    - [ ] E3: Build minimal Swift binary (load Hermes-3-8B, one completion, measure TTFT)
    - [ ] Verify MLX-Swift ecosystem checklist: prefix caching, SSE streaming, LoRA adapters, 4-bit quant
- [ ] **If pre-conditions pass**: Implement Swift inference library with Unix socket IPC to Go orchestrator
- [ ] **Feature Parity Check**:
    - [ ] Prefix caching (`--prompt-cache-size 2048` equivalent)
    - [ ] SSE streaming (required for OpenFang)
    - [ ] LoRA adapter loading (required for S4 multi-tenancy)

---

## Phase 17: Production Correctness Fixes ✅ COMPLETE (2026-04-06)

> All four items below fixed in `internal/server/handler.go` and `internal/supervisor/manager.go`.

- [x] **SSE-aware streaming proxy**: Replaced `io.Copy` with `bufio.ReadBytes('\n')` loop + `http.Flusher.Flush()`. OpenFang streaming TTFT now reflects actual first-token time. Non-streaming path unchanged.
- [x] **`/metrics` TTL cache**: `metricsCache` struct with 5s TTL eliminates subprocess churn. One `uv run python -c "..."` per monitoring interval instead of one per request.
- [x] **Maintenance drain race**: Added `inFlightCount int64` (atomic) to `EventHorizonServer`. `HandleCompletions` increments/decrements; `HandleMaintenance` polls until zero with 10s timeout. Drain is now real.
- [x] **`/v1/model/swap` 409 on contention**: Added `TrySwitchModel()` to `ProcessManager` (uses `swapMu.TryLock()`). Returns `ErrSwapInProgress`; handler maps to HTTP 409 with retry guidance. Implicit hot-swaps from `HandleCompletions` still use blocking `SwitchModel()`.

**To verify (operator):**
- `curl -N http://127.0.0.1:8000/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"...","stream":true,"messages":[...]}'` — tokens should arrive incrementally
- Poll `/metrics` rapidly for 10s — only one subprocess should spawn every 5s (check daemon.log)
- Enter maintenance mode, fire a completion request in parallel — request should drain before maintenance proceeds

---

## Phase 18: External Orchestration API ✅ COMPLETE (2026-04-06, Antigravity)

> **Dependency**: Required by both `llm-proving-ground` and `llm-factory` before either
> project can run evaluations or fine-tuning workflows through EHC. These projects need
> to signal EHC to enter a controlled state, swap in a specific model, and then resume
> normal operation — all without disrupting currently-running station agents.
>
> **Cross-project context**: See `llm-proving-ground/COEXISTENCE.md` and
> `llm-factory/COEXISTENCE.md` for the architectural rationale.

- [x] **`POST /system/maintenance`** — Enter maintenance mode
    - Accepts `{"reason": "string", "requested_by": "llm-proving-ground|llm-factory"}`
    - Sets an internal `maintenanceMode bool` flag (protected by `sync.RWMutex`)
    - All subsequent `/v1/chat/completions` requests immediately return `HTTP 503` with
      `Retry-After: 60` and `{"error":"EHC is in maintenance mode","retry_after":60}`
    - In-flight requests drain with a configurable grace period (default: 5s) before
      the flag flips
    - Returns `{"status":"maintenance","active_model":"<current>","since":"<timestamp>"}`
- [x] **`POST /system/maintenance/release`** — Exit maintenance mode
    - Accepts optional `{"promote_model": "<hf-model-id>"}` — if provided, the swapped-in
      model becomes the new default; if absent, EHC reverts to the pre-maintenance model
    - Clears the `maintenanceMode` flag; queued agents resume immediately
    - Returns `{"status":"operational","active_model":"<model>","promoted": true|false}`
- [x] **`GET /system/maintenance/status`** — Poll current state
    - Returns `{"in_maintenance": bool, "requested_by": "...", "since": "...", "active_model": "..."}`
    - Safe to call at any time; useful for proving ground / factory to confirm lock before starting
- [x] **`POST /v1/model/swap`** — Explicit model swap (usable inside or outside maintenance mode)
    - Accepts `{"model": "<hf-model-id>"}` — wraps existing `SwitchModel()` logic
    - Returns 409 if a swap is already in progress
    - This makes the hot-swap externally addressable, replacing ad-hoc model param tricks
- [x] **Add auth token check** to all `/system/*` endpoints
    - Read from `EHC_ADMIN_TOKEN` env var (set in `.env`, never committed)
    - Reject with `HTTP 401` if header `X-EHC-Admin-Token` is absent or wrong
    - Prevents accidental or malicious maintenance locks from untrusted callers
- [x] **Update `GET /status`** to include `maintenance_mode` and `maintenance_requested_by` fields
- [x] **`GET /metrics`** — MLX memory telemetry (add alongside maintenance API)
    - Shells out to `uv run python -c "import mlx.core; import json; print(json.dumps({'active_mb': mlx.core.metal.get_active_memory()//1024//1024, 'peak_mb': mlx.core.metal.get_peak_memory()//1024//1024}))"` within the EHC uv environment
    - Returns `{"active_mb": N, "peak_mb": N}` — used by proving ground for precise per-model VRAM readings
    - Proving ground falls back to `ioreg` polling if this endpoint is unavailable
- [x] **Add integration test** for the full proving-ground cycle:
    - `POST /system/maintenance` → confirm 503 on `/v1/chat/completions` → `POST /v1/model/swap`
      → run a test completion → `POST /system/maintenance/release` → confirm 200 resumes

---

## Phase 14: Quality/Goodness Framework [NOT STARTED]
- [ ] **Define Multi-Dimensional Benchmarks**:
    - [ ] **Tachyon Tongs (Firewall)**: Reasoning logic, prompt adherence, refusal robustness, MoE efficiency.
    - [ ] **Claw (Agent)**: Tool-calling precision, JSON schema adherence, TTFT (latency), context window utilization (128K+).
- [ ] **Create Prototype "Goodness Score"**:
    - [ ] Script to aggregate TPS, TTFT, and a weighted reasoning score into a single normalized value per hardware profile (M5 25GB).

---

## Phase 19: Memory Virtualization & Fragmentation Control [NOT STARTED]

> **Goal**: Achieve multi-model residency and instant cutover within the 24GB VRAM constraint.

- [ ] **Manual Memory Management**:
    - [ ] Investigate `MTLHeap` and `MTLBuffer` allocation patterns in the Metal backend.
    - [ ] Attempt to keep two "Small" models (e.g., 3B + 1B) resident in memory simultaneously.
- [ ] **KV Cache Offloading**:
    - [ ] Implement "Context Switching" for KV caches: swap inactive model caches to Unified System RAM to free up VRAM for the active generation.
- [ ] **Predictive De-fragmentation**:
    - [ ] Trigger memory compaction cycles before high-load agentic bursts.

---

---

## Phase 20: Advanced Hardware Telemetry [NOT STARTED]

- [ ] **Thermal-Aware Routing**:
    - [ ] Hook into `SMC` (System Management Control) for real-time M5 core temps.
    - [ ] Automatically route to smaller/cooler models if temps exceed 95°C to avoid heavy thermal throttling.
- [ ] **Unified Telemetry API**:
    - [ ] Consolidate VRAM, Thermal, and NPU/GPU utilization into a single management dashboard.

---

## Phase 21: Zero-Interruption Model Pre-warming [NOT STARTED]

> **Status Note**: We might consider this based on the outcome of prototyping MLX-Swift (Phase 16). If the Swift migration is successful, this Python-based multiplexing phase will be entirely deprecated in favor of native Swift memory threading.
>
> **Problem**: EHC's current hot-swap kills the running model and starts the new one
> synchronously on the first request that references it. This means:
> - Any agent mid-generation gets a 503 and must retry
> - Even idle agents see a 20-30s stall on their next message after a swap
> - There is no way to stage a model change in advance without affecting a running session
>
> **Solution**: Add a `POST /v1/preload` endpoint that loads a new model into memory in
> the background **without** stopping the currently-serving model. Once the new model
> reports healthy, EHC atomically cuts over — the running model serves until the last
> moment. Agents experience zero 503s; the only visible effect is a ~1s pause at
> cutover rather than a 20-30s stall.
>
> **Why this matters as the claw fleet grows**: With multiple agents running
> (ZeroClaw, OpenClaw, HermesAgent, etc.), an operator-initiated model swap today
> will 503 every active session simultaneously. Pre-warming makes model upgrades
> transparent to all running agents — load the new model in the background, cut over
> when it's hot, and no agent notices.

- [ ] Add `POST /v1/preload` handler in `internal/server/handler.go`
    - Accepts `{"model": "<hf-model-id>"}` body
    - **VRAM Budget Verification**: Calculate if model A + model B fits in 24GB. Reject if >22GB total to prevent OOM.
    - Launches background goroutine: starts a *second* mlx_lm.server instance on a
      temporary port, waits for HTTP `/health` to confirm it's ready
    - Returns `202 Accepted` immediately with `{"status":"preloading","model":"..."}`
- [ ] **Layer-Persistent Swapping**: If model architectures match, attempt to reuse base weights via symlinks or shared cache.
- [ ] Add `GET /v1/preload/status` to poll readiness of the warming model
    - Returns `{"status":"warming"|"ready"|"failed","model":"...","elapsed_secs":N}`
- [ ] On cutover: atomically swap the supervisor's active port from old → new,
      SIGKILL the old server's process group (existing in-flight requests drain first
      via a short grace period, e.g. 2s)
- [ ] Update `GET /status` to report both active model and any warming model
- [ ] Add test: preload model B while model A is serving, confirm A continues
      serving during warm-up, confirm cutover is seamless
- [ ] Document operator workflow in `README.md`:
    ```bash
    # Stage a model swap without interrupting running agents:
    curl -s -X POST http://127.0.0.1:8000/v1/preload \
      -H "Content-Type: application/json" \
      -d '{"model":"mlx-community/Qwen2.5-Coder-14B-Instruct-4bit"}'
    # Poll until ready:
    curl -s http://127.0.0.1:8000/v1/preload/status
    # Cutover happens automatically once ready
    ```

---

## Model Cache Inventory

> Last audited: 2026-04-05. Cache root: `~/.cache/huggingface/hub/`
> Total size at last audit: **49 GB** (after removing Qwen2.5-Coder-32B and incomplete Gemma 4 26B)
> To audit: `du -sh ~/.cache/huggingface/hub/models--* | sort -rh`

| Model | Size | Status | Decision |
|:------|:-----|:-------|:---------|
| `Qwen2.5-32B-Instruct-4bit` | 17 GB | Cached — not configured for active use | Review at next audit |
| `gemma-2-27b-it-4bit` | 14 GB | Cached — not configured for active use | Review at next audit |
| `Mistral-Nemo-Instruct-2407-4bit` | 6.4 GB | Cached — not configured for active use | Review at next audit |
| `gemma-4-e4b-it-4bit` | 4.9 GB | Cached — small Gemma 4 variant (4B active) | Keep — candidate for Tachyon Tongs/firewall profile |
| `Hermes-3-Llama-3.1-8B-4bit` | 4.2 GB | **Active** — EHC default model | Keep |
| `Llama-3.2-3B-Instruct-4bit` | 1.7 GB | Cached — draft model candidate for speculative decoding | Keep |
| `Llama-3.2-1B-Instruct-4bit` | 680 MB | Cached — draft model candidate | Keep |
| `Qwen2.5-Coder-32B-Instruct-4bit` | — | **Removed 2026-04-05** — OOMs on 24GB M5 during generation | — |
| `gemma-4-26b-a4b-it-4bit` | — | **Removed 2026-04-05** — incomplete download (mlx-lm unsupported) | Re-download when mlx-lm >= 0.32.x |

**Pending downloads:**
- `mlx-community/Qwen2.5-Coder-14B-Instruct-4bit` (~8.8 GB) — target coding model for ZeroClaw (see claws/zeroclaw/TASKS.md)
- `mlx-community/gemma-4-26b-a4b-it-4bit` (~15.6 GB) — re-download when mlx-lm >= 0.32.x + PR #1112 closed
