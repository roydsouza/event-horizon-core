# Event Horizon Core: Tasks

> **This is the single contract between Roy, Claude Code, and AntiGravity.**
> Mark in-progress with `[/]`, complete with `[x]`. Never mark done without verification.
> A `[/]` marker means the other agent has this task — do not touch it.
>
> **Cross-references:** [LIMITATIONS.md](LIMITATIONS.md) (why) · [ROADMAP.md](ROADMAP.md) (where) · [SOLUTIONS.md](SOLUTIONS.md) (how)

---

## 🔁 Recurring Tasks

> Check on every session open. If `Next Due` ≤ today, surface to Roy before starting any other work.
> After completing, update `Next Due` by adding the interval to today's date.

| Frequency | Next Due | Task | Notes |
|:----------|:---------|:-----|:------|
| Weekly | 2026-04-25 | **Model cache audit** — `du -sh ~/.cache/huggingface/hub/models--* \| sort -rh`. Evict unused models, cross-check with `llm-proving-ground/reports/cache-manifest.md`. | Current inventory: see Model Cache section below |
| Weekly | 2026-04-25 | **Default model evaluation** — is there a better single-model candidate than `Hermes-3-Llama-3.1-8B-4bit`? Primary candidate: Gemma 4 26B A4B (ready as of `mlx-lm >= 0.32.x`). Check readiness: `uv run python3 -c "from mlx_lm.models import gemma4; print('ready')"` | Gemma 4 readiness verified 2026-04-18. |
| Monthly | 2026-05-07 | **MLX multiplexing options re-evaluation** — update `docs/research/MLX_MULTIPLEXING_OPTIONS.md` with current state of mlx-lm, vllm-mlx, oMLX, vllm-metal; run any experiments needed; decide if hot-swap / multi-model strategy should be adopted. | Hot-swap deferred 2026-04-07; see Phase 15 for context |

---

## 🟡 Active / Next

### Phase 13: Gemma 4 Default Model Evaluation — ACTIVE
> **Addresses:** [L7](LIMITATIONS.md#l7-lack-of-structured-observability) (partial) · **Goal:** Evaluate Gemma 4 as a *replacement candidate* for the single default model slot (Hermes-3-8B-4bit). Promote only if it outperforms Hermes on both TTFT and TPS under 3-client load on the M5 24 GB.
>
> **Status:** `mlx-lm >= 0.32.x` is available and supports the `gemma4` architecture.

- [x] Confirmed `mlx-lm 0.31.x` lacks gemma4 architecture
- [x] Post-Gemma rollback complete: stable `mlx-lm==0.31.1` reinstalled, Go binary rebuilt
- [ ] Update `pyproject.toml` to `mlx-lm>=0.32.0` to enable gemma4 support
- [ ] Download `mlx-community/gemma-4-e4b-it-4bit` (already cached — 4.9 GB) and `mlx-community/gemma-4-26b-a4b-it-4bit` (~15.6 GB)
- [ ] Single-client benchmarking: TTFT and TPS vs. Hermes-3-8B-4bit baseline (use `llm-proving-ground`)
- [ ] 3-client concurrent load test: confirm stability and VRAM headroom on 24 GB M5
- [ ] **Decision gate:** if Gemma 4 wins on TTFT + TPS → promote as new default and retire Hermes; otherwise keep Hermes

### Phase 27: Tier 2 (Free) Integration — Gemma 4 (Google AI Studio)
> **Addresses:** [L11] (Lack of high-reasoning free tier) · **Goal:** Provide zero-cost access to Gemma 4 via Google AI Studio when using the `--model free` alias.
>
> **Technical Plan:** Implement a dedicated Go provider for Google's Generative AI API and route requests matching the "free" alias to it, bypassing the local MLX supervisor.

- [ ] Obtain Google AI Studio API Key and add `GOOGLE_AI_API_KEY` to `.env`
- [ ] Implement `GoogleGenerativeAIProvider` in a new `internal/providers/` package
- [ ] Update `HandleCompletions` in `internal/server/handler.go` to intercept `model: "free"` requests
- [ ] Implement SSE streaming support for the Gemini provider (matching Phase 17 standards)
- [ ] Add integration test in `tests/stress_test.go` to verify remote routing
- [ ] Update `CHEATSHEET.md` to reflect active status of Tier 2

### Phase 28: Integrated Proving Ground Workflow
> **Goal:** Exercise co-existence and high-integrity model promotion by integrating EHC with `llm-proving-ground`.
>
> **Workflow:** Simulate a production station where a client is running while a background evaluation/promotion cycle occurs.

- [ ] Create/Run a representative client (e.g. `tests/dummy_agent.py`) actively consuming the EHC Port 8000
- [ ] Trigger `llm-proving-ground` to download a new candidate model
- [ ] **Acquire Maintenance Lock**: `llm-proving-ground` requests `/system/maintenance` on EHC (graceful client stall)
- [ ] **Swap Candidate**: `llm-proving-ground` swaps the candidate into Port 8080 via EHC
- [ ] **Evaluation Suite**: Run full benchmarking harnesses through EHC routes
- [ ] **Signal Decision**: Automated prompt to Roy to either **Promote** (sets new default) or **Revert** (unloads candidate)
- [ ] Verify transition back to operational state for the original representative client

### Phase 24: Agent Identity, Observability & Firewall Hook — IN PROGRESS
> **Addresses:** Observability, firewall interception · **Roadmap:** [R8](ROADMAP.md#r8-agent-identity-per-client-routing--firewall-interception) · **Solution:** [S16](SOLUTIONS.md#s16-agent-identity--per-client-routing-proposed--phase-24)

- [ ] **DEFERRED — Config-file routing table** (`config.toml`, per-agent model pins, `SIGHUP` hot-reload): revisit when monthly MLX review adopts multi-model strategy.

---

## 🔴 On Hold

### Phase 16: MLX-Swift & Native Migration — ❌ NO-GO BASED ON E1
> **E1 result (2026-04-07):** Cold-cache Python overhead is **5–11%** of total swap time — well below the 30% gate. Weight loading (1.6–3.6s) dominates and is language-independent. Swift migration saves ~200ms on a 1.9–3.8s operation. Not worth the ecosystem risk or reimplementation cost.
>
> **Gate status:** Gate 1 FAILS on cold-cache data. Do not proceed to E3. Revisit only if system characteristics change materially (e.g. 48 GB+ hardware where cold loads become fast enough that Python overhead is proportionally larger).
>
> **Original gate (for reference):** E1 Python overhead >30% AND E3 Swift TTFT <2s → greenlight. Neither condition met for the real-world cold-cache case.

- [x] E1 instrumentation complete; data in `benchmarks/swap_latency.csv`
- [x] NO-GO decision recorded in LIMITATIONS.md L1 and ROADMAP.md R2/R4

---

## ⚪ Not Started (ordered by priority)

### Phase 19: Memory Virtualization — LOW PRIORITY · partially superseded
> **Note:** KV Cache Offloading (original Phase 19 sub-task) is not applicable on Apple Silicon — "system RAM" and "VRAM" are the same physical pool. See [LIMITATIONS.md L5-B](LIMITATIONS.md#l5-vram-fragmentation). The relevant memory work is now Phase 23 (pressure monitoring) and Phase 26 (idle unloading).

- [ ] Investigate `MTLHeap`/`MTLBuffer` allocation patterns in the Metal backend — assess whether two small models (3B + 1B) can coexist in 24 GB
- [ ] ~~KV Cache Offloading~~ — **not applicable on Apple Silicon unified memory** (see L5-B)
- [ ] ~~Predictive De-fragmentation~~ — **MLX manages its own allocator; external compaction not exposed**

### Phase 20: Advanced Hardware Telemetry
> **Dependency:** Phase 23 (memory pressure) should land first to establish the telemetry pattern.

- [ ] Hook into SMC for real-time M5 core temperatures; auto-route to smaller model if > 95°C
- [ ] Unified telemetry API: consolidate VRAM, thermal, NPU/GPU utilisation into one endpoint

### Phase 21: Zero-Interruption Model Pre-warming — DEFERRED · not applicable to single-model strategy
> **Status:** Not applicable under the single-model strategy adopted 2026-04-07. Pre-warming exists to hide hot-swap latency — hot-swap is now deferred entirely. Phase 16 is NO-GO. On the 24 GB M5 running two models simultaneously requires >9 GB headroom we don't have.
>
> **Revisit only if:** (a) monthly MLX review adopts multi-model routing AND (b) E1 data shows swap latency is unacceptable for the use case at that time. Do not implement prewarming before multi-model strategy is confirmed.

- [ ] `POST /v1/preload` — load new model in background on a temporary port without stopping the current model
    - VRAM budget check: reject if model A + model B > 22 GB
    - Returns `202 Accepted` immediately; poll `GET /v1/preload/status` for readiness
- [ ] Atomic port cutover once warm model is healthy; drain in-flight requests (2s grace period)
- [ ] `GET /status` update to report warming model alongside active model

---

## ✅ Complete

### Phase 22: Cold-Start Instrumentation (Experiment E1) ✅ COMPLETE (2026-04-07)
- [x] Instrument `manager.go` — checkpoints at SIGKILL, uv start, first health poll, ready; CSV to `benchmarks/swap_latency.csv`
- [x] Hot-cache measurement run (2026-04-06): 258–357ms total, Python 57–79%
- [x] Pressure-cold measurement run (2026-04-07, incidental, ~2 GB free): 1,877–3,807ms total, Python 5–11%
- [x] Controlled cold measurement run (2026-04-07, sudo purge, 13.7 GB free): 1,263–1,469ms total, Python 14–16% — 6 swaps, consistent
- [x] LIMITATIONS.md L1 updated with three-scenario table and FINAL NO-GO verdict
- [x] LIMITATIONS.md L10 (Unified Memory Pressure) added
- [x] NO-GO recommendation confirmed in Phase 16 banner

### Phase 23: Unified Memory Pressure Monitoring ✅ COMPLETE (2026-04-07)
- [x] **`/system/memory` endpoint** (`handler.go`) — [S15](SOLUTIONS.md#s15-system-memory-endpoint-proposed--near-term)
- [x] **Memory pressure guardrail** (`manager.go`)
- [x] Verify `/system/memory` and swap rejection under pressure (2026-04-07)

### Phase 23-GW: Phase 23 Get-Well Items ✅ COMPLETE (2026-04-07)
- [x] **`/system/memory` auth gate removed**
- [x] **`MemoryStats.Speculative` renamed to `SpeculativeMB`**
- [x] **`verify_metrics_ttl.py` + `verify_drain.py` .env path fixed**
- [x] **Proactive memory pressure logging** (`handler.go`)
- [x] **`docs/MEMORY_RUNBOOK.md`**

### Phase 26: Idle Model Unloading ✅ COMPLETE (2026-04-07)
- [x] `lastRequestNano int64` + `idleSince int64` (atomic) added to `EventHorizonServer`
- [x] `idleMonitor()` goroutine in `Start()`
- [x] `EnsureRunning(ctx)` on `ProcessManager`
- [x] Config: `EHC_IDLE_TIMEOUT_SECONDS` env var
- [x] `"idle_since"` field in `GET /status` response
- [x] **Operator test verified 2026-04-07**
- [x] Trade-off documented in `docs/MEMORY_RUNBOOK.md`

### Phase 15: Concurrency Correctness & Multiplexing Research ✅ COMPLETE (2026-04-07)
- [x] Fix hot-swap race condition in `ProcessManager`
- [x] Document MLX multiplexing alternatives in `docs/research/MLX_MULTIPLEXING_OPTIONS.md`
- [x] Verify upstream mlx_lm bug status — #965 + #754 fixed in 0.31.2
- [x] Research complete — all open questions answered
- [x] mlx-lm upgraded to `>=0.31.2,<0.32`
- [x] **Decision recorded:** hot-swap deferred; single-model focus

### Phase 25: Structured Observability (slog) ✅ COMPLETE (2026-04-07)
- [x] Replace all `log.Printf` calls with `slog`
- [x] Emit structured JSON log lines
- [x] Add `X-Request-ID` response header
- [x] Add in-memory event ring buffer
- [x] Add structured log fields to swap events

### Phase 14: Quality / Goodness Framework ✅ COMPLETE (2026-04-07)
- [x] Define multi-dimensional benchmarks
- [x] Prototype "Goodness Score"

### Phase 24 (Partial Content): Agent Identity, Observability & Firewall Hook ✅ PARTIAL (2026-04-07)
- [x] **⚡ PRIORITY (no code needed) — Retrofit `X-Agent-Name` header into setup guides**
- [x] **`X-Agent-Name` parsing** in `HandleCompletions`
- [x] **Per-agent in-memory metrics**
- [x] **Firewall interception hook**

### Phase 18: External Orchestration API ✅ COMPLETE (2026-04-06)
- [x] Implement maintenance and swap endpoints

### Phase 17: Production Correctness Fixes ✅ COMPLETE (2026-04-06)
- [x] SSE-aware streaming proxy
- [x] `/metrics` TTL cache
- [x] Maintenance drain race fix
- [x] `/v1/model/swap` 409 return
- [x] **Operator verification complete**

### Phases 1–12 ✅ COMPLETE (archived)
<details>
<summary>Click to expand</summary>
(Table of previous phases)
</details>

---

## Model Cache Inventory

> Last audited: 2026-04-07. To re-audit: `du -sh ~/.cache/huggingface/hub/models--* | sort -rh`
> **Total: 11.6 GB** (37.4 GB freed this session)

| Model | Size | Status | Notes |
|:------|:-----|:-------|:------|
| `Hermes-3-Llama-3.1-8B-4bit` | 4.2 GB | **Active — EHC default** | Keep |
| `gemma-4-e4b-it-4bit` | 4.9 GB | Cached | Firewall profile candidate; keep |
| `Llama-3.2-3B-Instruct-4bit` | 1.7 GB | Cached | E1 swap test model; draft candidate; keep |
| `Llama-3.2-1B-Instruct-4bit` | 680 MB | Cached | Draft candidate; keep |

**Pending downloads (do not download without Roy approval):**
- `mlx-community/Qwen2.5-Coder-14B-Instruct-4bit` (~8.8 GB) — ZeroClaw coding model candidate
- `mlx-community/gemma-4-26b-a4b-it-4bit` (~15.6 GB) — re-download when mlx-lm >= 0.32.x + PR #1112 merged
