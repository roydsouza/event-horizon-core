# Event Horizon Core: Tasks

## 🔁 Recurring Tasks

> **Opening ritual for both agents**: On every session open, check the table below.
> If `Next Due` ≤ today, surface the item to the operator before starting other work.
> After completing a recurring task, update `Next Due` by adding the interval to today's date.

| Frequency | Next Due | Task | Notes |
|:----------|:---------|:-----|:------|
| Weekly | 2026-04-12 | **Model cache audit** — review `~/.cache/huggingface/hub/`, decide what to keep/remove. Cross-check with `llm-proving-ground/reports/cache-manifest.md` for evaluation downloads. | See "Model Cache Inventory" section below for current state |
| Weekly | 2026-04-12 | **Gemma 4 26B A4B readiness check** — is `mlx-lm >= 0.32.x` on PyPI? Is PR #1112 closed? | `uv run python3 -c "from mlx_lm.models import gemma4; print('ready')"` and check https://github.com/ml-explore/mlx-lm/pull/1112 |

---

## Phase 1: Environment & Setup [MUST COMPLETE]
- [x] **OpenRouter Activation**:
    - [x] Obtain API Key from [OpenRouter.ai](https://openrouter.ai/keys).
    - [x] Copy `.env.template` to `.env`.
    - [x] Add `OPENROUTER_API_KEY="your_actual_key"` to your `.env` file. (Fixed environment loading in CLI).
- [x] **uv Transition**:
    - [x] Install `uv` (Fastest Python package manager).
    - [x] Run `uv sync` to build the synchronized `.venv`.
    - [x] Verify with `uv run event-horizon status`.

## Phase 2: Performance & Connectivity [COMPLETE]
- [x] VRAM Guard implementation (24GB limit enforcement).
- [x] OpenRouter remote fallback provider.
- [x] Comprehensive CLI `--help` with examples.
- [x] Agent Setup Guides (OpenClaw, ZeroClaw, OpenCode, etc.).
- [x] Repository security (`.gitignore` for secrets).

## Phase 3: Concurrency Torture Testing [COMPLETE]
- [x] Create `tests/test_torture.py` (Pytest-asyncio suite).
- [x] Baseline Benchmark: Run torture tests and document failures/latencies.
- [x] Monitor GPU/VRAM behavior: Observed M5 performance under 5x concurrent load.
    - **Finding**: Ollama internal queueing works but triggers 60s client timeouts.
    - **Finding**: MLX is stable for serial/low-concurrency but lacks cross-agent locking.
    - **VRAM**: Guard at 22GB is effective; OS remained stable during saturation.

## Phase 4: Orchestration & Resource Optimization [COMPLETE]
- [x] **Research & Selection Findings**:
    - **Note**: Benchmarked `mlx_lm.server` (v0.31.1). Results showed 60% speedup on cached prompts and native 100% success on multi-process serialization.
    - **Decision**: Pivoting to raw `mlx_lm.server` as the primary local substrate. This natively solves "Cross-process Locking" and "Advanced Persistence" without custom EH-Orchestrator overhead.
    - **Paths Not Taken (and Why)**:
        - **vllm-mlx**: Bypassed. While powerful (Continuous Batching), it is currently a third-party port and 0.31.1 of the official server now includes the critical `prompt-cache-size` and `decode-concurrency` features with better stability.
        - **oMLX**: Bypassed for now. Its SSD-swapping is excellent, but for 24GB on M5, the official in-RAM prompt cache is sufficient for 4-5 active agents. We will revisit if VRAM becomes a critical bottleneck.
        - **Sluice-LLM / llama-swap**: Bypassed. These were considered as proxy layers to handle locking, but since `mlx_lm.server` implements internal serialization, adding another proxy layer adds unnecessary latency.
        - **Custom KV Swap Implementation**: Bypassed. Implementing `make_prompt_cache` and `mx.save_safetensors` manually in our provider is redundant now that the server handles it via JSON-RPC/REST.
- [x] **Initial Orchestration Implementation**:
    - [x] Developed **`LocalInferenceQueue`** (Foundational; replaced by native server).
    - [x] Integrated **Orchestrator** into CLI for basic traffic management.
    - [x] Optimized Provider Timeouts (300s).
- [x] **Research: mlx_lm.server as native backend**:
    - [x] **Replace custom Orchestrator/Locking**: Confirmed. Native server handles continuous batching and multi-process safety.
    - [x] Test OpenAI-compatible endpoints: Verified (`/v1/chat/completions`).
    - [x] Verify `--prompt-cache-size`: Confirmed 60% latency reduction.
- [x] **Advanced Persistence & Context Swapping**:
    - [x] Handled implicitly by `mlx_lm.server`'s KV Cache manager.
- [x] **Dynamic Failover Upgrade**:
    - [x] Integrated into CLI logic (MLX Server -> Ollama -> OpenRouter).

## Phase 5: Native Architecture Integration [COMPLETE]
- [x] **Refactor MLX Backend**: 
    - [x] Implementation: Refactor `MLXProvider` into `RemoteNativeProvider` wrapping `mlx_lm.server`.
    - [x] Verification: Test concurrent multi-agent requests via CLI. (Confirmed 1.53s avg latency).
- [x] **Extended Capabilities [PHASE 5.2]**:
    - [x] **OpenRouter Model Shorthand**: Implement aliasing.
    - [x] Performance benchmark script (tok/s logger).
- [x] **Native Llama.cpp & Ollama (DECOMISSIONED)**:
    - [x] Logic removed in Streamlining Phase to focus on pure MLX performance.

## Phase 6: Substrate Streamlining (MLX-Only) [COMPLETE]
- [x] **Pivot to Pure MLX**:
    - [x] Removed Tier 2 (Llama.cpp) and Tier 4 (Ollama) from Go substrate.
    - [x] Optimized for 24GB M5 VRAM by specializing on MLX native Metal bindings.

## Phase 7: Go Substrate Migration & Advanced Optimization [COMPLETE]
> <gemini_action_item: flash_model> **FLASH INSTRUCTIONS**: Initialize a `go.mod` project. Use *only* the `net/http` standard library for routing. Do not use external web frameworks. Follow the exact specs below.
- [x] **Architecture (Zero-Dependency Daemon)**:
    - [x] Initialize Go codebase using Go 1.22+ standard library (`net/http`) for minimal memory footprint and zero external proxy dependency.
    - [x] Port the Provider Fallback Hierarchy (MLX -> Llama.cpp -> OpenRouter) to highly concurrent Goroutines.
- [x] **Active Native Server Supervision & Zombie Recovery**:
    - [x] Implement Go subprocess management (`os/exec`) to dynamically launch, monitor, and instantly restart native servers if they crash (Crash Loop Backoff).
    - [x] **Anti-Zombie Mutex**: Bind `mlx_lm.server` and `llama-server` to independent Process Groups (`syscall.Setpgid`). Add a recovery listener in Go to broadcast a `SIGKILL` to the entire process group tree upon proxy exit, guaranteeing 0 VRAM leaks.
- [x] **Dynamic Model Swapping**:
    - [x] Implement Go HTTP middleware to intercept model mismatches.
    - [x] Safely Hot-Swap Models: Gracefully bounce the active MLX server to load the new weights while blocking the client connection, preventing 502 errors.
- [x] **OS-Level Integration (macOS launchd)**:
    - [x] Create `build/com.antigravity.eventhorizon.plist` configuration.
    - [x] Register Event Horizon Core as an invisible, self-healing background service mapped permanently to Port `8000` via `launchctl`, ensuring it starts silently on M5 boot.
- [x] **OpenRouter Go Provider (Tier 3)**:
    - [x] Implement internal/providers/openrouter.go with model aliasing (best, fast, free).
- [x] **Client Interop & Migration**:
    - [x] Standardize local REST API (exposed on `127.0.0.1:8000`).
    - [x] Draft migration instructions/scripts for Python clients (Tachyon Tongs, ZeroClaw, OpenFang) to transition from `LLMFactory` imports to asynchronous HTTP calls.
- [x] **Algorithmic Hardware Optimizations**:
    - [x] **Prefix Caching**: Inject `--prompt-cache-size` at supervised launch to radically reduce TTFT (Time-To-First-Token) for multi-agent workflows sharing System Prompts.
    - [x] **Speculative Decoding**: Inject `--draft-model` configuration, allowing a small 1B model to parallel-draft tokens for the primary model on the M5.

## Phase 8: Acceptance Criteria & Rigorous Test Plan [COMPLETE]
> <gemini_action_item: flash_model> **FLASH INSTRUCTIONS**: Build a rigorous Go test suite (`*_test.go`) or a robust Python async test script to hit the endpoints and verify VRAM isn't leaking.
- [x] **Stress Test Suite**: Create a high-concurrency request generator to bombard port `8000` with 50+ simultaneous agent queries. Confirm `mlx_lm.server` handles continuous batching natively without the Go proxy dropping sockets.
- [x] **Zombie Process Verification**: Intentionally crash the Go Proxy (`kill -9`) and verify via `ps aux | grep mlx` that the OS cleanly destroyed the child processes due to the Process Group bindings.
- [x] **Model Swap Verification**: Rapidly request `Model A`, then `Model B`, then `Model A`. Verify the Go proxy buffers the connections and no 502 Bad Gateway errors are returned to the client during the swapping latency.
- [x] **Latency Benchmark**: Time-To-First-Token (TTFT) through the Go Proxy must not exceed +50ms over a direct request to the underlying `mlx_lm.server`.

## Phase 9: Python Eradication & Code Cleanup [COMPLETE]
- [x] Delete `event_horizon_core/orchestrator.py`.
- [x] Delete all provider implementations `event_horizon_core/providers/*.py`.
- [x] Strip `pyproject.toml` and `uv.lock` of any dependencies no longer needed by the core (e.g., `httpx`), retaining only what is needed for `mlx-lm` installation.
- [x] Remove `main.py` entrypoints if applicable and officially transition the repository root to the Go structure.
- [x] Close out `TASKS.md` Phase 9 as Complete.

## Phase 10: Local-Only Simplification (Minimal Attack Surface) [COMPLETE]
- [x] **Pare everything down to MLX Local only**:
    - [x] Remove `OpenRouter` client and routing from `internal/server/handler.go`.
    - [x] Delete `internal/providers/openrouter.go`.
    - [x] Clean up CLI documentation in `event_horizon_core/cli.py`.
    - [x] Update `README.md` and `MODELS.md` to reflect local-only architecture.
    - [x] Remove `OPENROUTER_API_KEY` from environment templates and Go logic.

## Future Roadmap: Remote Frills & Orchestrated Reviews
- [ ] **Re-integrate OpenRouter for Unified Interop**:
    - [ ] Implement remote engine as a secondary tier (remote/best, remote/fast).
    - [ ] Develop "Seamless Fallback": Automatically route to remote providers when local VRAM is saturated or M5 thermal throttles.
- [ ] **Multi-Agent Review Cycles**:
    - [ ] Local model acts as primary author; reaches out to remote models (Claude/Gemini) for critical reviews, arguments, and counter-points.
    - [ ] Unified interface for comparing local MLX output with remote reasoning models.
- [ ] **Advanced Concurrency & KV Caching**:
    - [ ] Implement the [Concurrency Architecture](docs/research/concurrency_architecture.md) blueprint for multi-agent VRAM efficiency.
    - [ ] Leverage [M5 Model Benchmarks](docs/research/model_benchmarks_m5.md) to optimize local-only agentic performance.

## Phase 11: Hardware Performance & SLO Verification [COMPLETE]
- [x] **New Performance Suite**: 
    - [x] Create `tests/hardware_benchmark.py` (Async TTL/TPS Metrics).
    - [x] Delete legacy `tests/test_torture.py`.
- [x] **Stress Test Calibration**:
    - [x] Run 10-client concurrency benchmarks on M5 Silicon. (Result: 0.74s P95 TTFT).
    - [x] Measure Model Swap latency (Hot-Swap) between 3B and 1B models. (Result: 1.93s Max).
- [x] **Service Level Objectives (SLOs)**:
    - [x] Establish "Operational Guardrails" section in `README.md`.
    - [x] Document P95 TTFT and TPS targets for hardware-native inference.

## Phase 12: LLM Candidate Evaluation [COMPLETE]
- [x] **Decode & Normalize Candidates**:
    - [x] Map fictitious 2026 models from `GUIDANCE.md` to the closest existing high-performance MLX model repos (see `tests/benchmark_candidates.py` CANDIDATES dict).
    - Mapped 5 candidates: Qwen2.5-Coder-32B, Qwen2.5-32B, Hermes-3-8B, Gemma-2-27B, Mistral-Nemo-12B.
- [x] **Download & Exercise Base Images**:
    - [x] Pre-fetch quantized weights for all 5 models (via `huggingface_hub.snapshot_download`).
    - [x] Verify basic completions against standard prompts — 3/5 succeeded, 2/5 failed (Gemma crashed, Mistral 503).
- [x] **Load & Swap Testing**:
    - [x] Run 5-client concurrency thresholds against all candidates.
    - [x] Perform hot-swap baseline across multi-GB model loads.
    - Results: Only Hermes-3-8B-4bit viable (27.9 single TPS, 14.1 under 5-client pressure). All 32B/27B models deadlocked under concurrent load.
- [x] **System Load Profiling**:
    - [x] Configure `asitop` across 5-client concurrency windows to monitor true memory/bus load for surviving candidates.
- [x] **Data Finalization**:
    - [x] Aggregate findings for initial candidates into `docs/research/llm_candidate_results.md`.
    - [x] Update results with Gemma 4 data (Phase 13).

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

### Phase 12 Key Finding
> **On 24GB M5, multi-agent workloads are strictly limited to the 8B parameter tier.** 32B models fit in VRAM but KV cache expansion under 5-client load breaches the 22GB guard, causing 0.0 TPS deadlock. The **Hermes-3-Llama-3.1-8B-4bit** is the only tested model that maintains double-digit TPS under pressure.

- [/] **Stale `/status` response**: Go daemon returns `"openrouter":true` in JSON despite OpenRouter removal in Phase 10. Rebuild the `event-horizon` binary from current source.

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
- [ ] **Verify upstream mlx_lm bug status**: Check if #965, #754, #883 are fixed in current
    `pip install mlx_lm`. If fixed, no backend change needed. Run: `uv run pip show mlx_lm`
    and check its changelog against the issue numbers.
- [ ] **Operator reviews** `docs/research/MLX_MULTIPLEXING_OPTIONS.md` and decides direction
- [ ] **Implement chosen direction** (TBD — see research doc)

## Phase 16: Zero-Interruption Model Pre-warming [NOT STARTED]

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
    - Launches background goroutine: starts a *second* mlx_lm.server instance on a
      temporary port, waits for HTTP `/health` to confirm it's ready
    - Returns `202 Accepted` immediately with `{"status":"preloading","model":"..."}`
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

## Phase 17: Streaming Proxy Correctness [NOT STARTED]

> **Discovered during OpenFang integration (2026-04-05)**
>
> EHC's current `HandleCompletions` uses `io.Copy(w, resp.Body)` to proxy responses. For
> non-streaming requests this is correct. For SSE streaming (`stream: true`), `io.Copy`
> uses a 32KB internal buffer — chunks from mlx_lm.server accumulate until the buffer
> fills before being flushed to the client. This turns real-time token streaming into
> a near-batch delivery from the client's perspective.
>
> **Impact**: OpenFang uses `stream: true` by default. Functionally correct (response
> arrives eventually) but TTFT appears as full-generation time rather than first-token time.
> IronClaw and ZeroClaw use non-streaming — not affected.
>
> **Fix**: Cast `ResponseWriter` to `http.Flusher` and call `Flush()` after each `io.Copy`
> chunk, or use a custom SSE-aware copy loop.

- [ ] Implement SSE-aware streaming proxy in `HandleCompletions`:
  - Cast `w` to `http.Flusher`; call `Flush()` after each write
  - Alternatively: line-buffered copy loop that flushes on `\n\n` boundaries
  - Preserve current non-streaming path unchanged
- [ ] Test: `curl -N http://127.0.0.1:8000/v1/chat/completions` with `"stream": true` — confirm tokens arrive incrementally
- [ ] Benchmark: TTFT should match direct mlx_lm.server call within +5ms

---

## Phase 18: External Orchestration API [NOT STARTED]

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
