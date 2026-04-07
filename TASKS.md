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
| Weekly | 2026-04-12 | **Model cache audit** — `du -sh ~/.cache/huggingface/hub/models--* \| sort -rh`. Evict unused models, cross-check with `llm-proving-ground/reports/cache-manifest.md`. | Current inventory: see Model Cache section below |
| Weekly | 2026-04-12 | **Gemma 4 26B A4B readiness check** — is `mlx-lm >= 0.32.x` on PyPI? Is PR #1112 closed? | `uv run python3 -c "from mlx_lm.models import gemma4; print('ready')"` |

---

## 🟡 Active / Next

---

### Phase 22: Cold-Start Instrumentation (Experiment E1) — PARTIAL

> **Addresses:** [L1](LIMITATIONS.md#l1-cold-start-model-swap-latency) · **Solution:** [S15 (data)](SOLUTIONS.md)
> **Key finding:** Cold-cache swaps (the real-world case) show Python overhead at only 5–11% — Phase 16 (Swift) gate is **NO-GO**. See LIMITATIONS.md L1.

- [x] Instrument `manager.go` — checkpoints at SIGKILL, uv start, first health poll, ready; CSV to `benchmarks/swap_latency.csv`
- [x] Hot-cache measurement run (2026-04-06): 258–357ms total, Python 57–79%
- [x] Cold-cache measurement run (2026-04-07, incidental): 1,877–3,807ms total, Python 5–11%
- [x] LIMITATIONS.md L1 updated with two-scenario table and NO-GO verdict for Phase 16
- [x] LIMITATIONS.md L10 (Unified Memory Pressure) added
- [ ] **REMAINING** — Run controlled cold measurement: `sync && sudo purge`, then 5× each direction. **STALLED (System OOM crash 2026-04-07). SAFETY RULE: stop EHC and close browser before running — issuing `sudo purge` with MLX model loaded caused the crash.**
- [ ] **REMAINING** — Confirm NO-GO recommendation is written into Phase 16 banner.

---

### Phase 23: Unified Memory Pressure Monitoring ✅ COMPLETE (2026-04-07)

> **Addresses:** [L10](LIMITATIONS.md#l10-unified-memory-pressure--non-compressible-metal-allocations--high-mac-freeze-risk) · **Solutions:** [S14](SOLUTIONS.md#s14-macos-memory-pressure-hook-proposed--medium-term), [S15](SOLUTIONS.md#s15-system-memory-endpoint-proposed--near-term)
> **Key finding:** Native `vm_stat` parsing in Go identifies critical pressure (< 1GB free) and successfully aborts model swaps to prevent kernel-level UI freezes.

- [x] **`/system/memory` endpoint** (`handler.go`) — [S15](SOLUTIONS.md#s15-system-memory-endpoint-proposed--near-term)
    - [x] Parse `vm_stat` output in Go; return JSON with pressure state
    - [x] Thresholds: warn < 2048 MB free, critical < 1024 MB free
- [x] **Memory pressure guardrail** (`manager.go`)
    - [x] Integrated `GetMemoryStats` into `doSwitch`
    - [x] Abort swap with error if pressure is `critical`
- [x] Verify `/system/memory` and swap rejection under pressure (2026-04-07)

---

### Phase 23-GW: Phase 23 Get-Well Items — PARTIAL

> Post-crash review (2026-04-07, Claude Code) surfaced three correctness issues in AntiGravity's Phase 23 delivery, plus two missing spec items that were dropped.

- [x] **`/system/memory` auth gate removed** — endpoint moved off `adminAuthMiddleware`; it is an observability primitive like `/status`, not an admin action. Required for Phase 26 idle-unloading health checks without credential plumbing.
- [x] **`MemoryStats.Speculative` renamed to `SpeculativeMB`** — field name now consistent with all other struct fields; JSON key unchanged (`speculative_mb`).
- [x] **`verify_metrics_ttl.py` + `verify_drain.py` .env path fixed** — `"event-horizon-core/.env"` → `".env"` (scripts run from project root)
- [x] **Proactive memory pressure logging** (`handler.go`) — `pressureMonitor()` goroutine launched from `Start()`: polls every 30s, logs on state transitions only (no spam). `[WARN memory-pressure]` / `[INFO memory-pressure]` in daemon.log.
- [x] **`docs/MEMORY_RUNBOOK.md`** — operator runbook: pressure state table, log indicators, freeze runbook, pre-benchmark checklist (stop EHC + close browser before `sudo purge`), Phase 26 trade-off table.

---

### Phase 26: Idle Model Unloading — ACTIVE · highest-impact freeze mitigation

> **Moved from Not Started to Active (2026-04-07, post-crash review).** This is the single highest-impact structural fix for Mac freezing. Phase 23's guardrail prevents making things worse; this phase actually returns the ~4.6 GB Metal allocation to the system during idle periods. E1 data confirms cold-start penalty is 1.9–3.8s — acceptable for current usage patterns.
>
> **Addresses:** [L10](LIMITATIONS.md#l10-unified-memory-pressure--non-compressible-metal-allocations--high-mac-freeze-risk) · **Solution:** [S13](SOLUTIONS.md#s13-idle-model-unloading-proposed--medium-term)

- [x] `lastRequestNano int64` + `idleSince int64` (atomic) added to `EventHorizonServer`; `lastRequestNano` updated on every `HandleCompletions` entry
- [x] `idleMonitor()` goroutine in `Start()`: checks every 60s; calls `pm.IdleUnload()` if idle > timeout; `IdleUnload` serialized through `swapMu` to prevent race with `EnsureRunning`
- [x] `EnsureRunning(ctx)` on `ProcessManager`: restarts stopped model; waits if already starting; no-op if running. Called from `HandleCompletions` when `StatusStopped` detected.
- [x] Config: `EHC_IDLE_TIMEOUT_SECONDS` env var (default `0` = disabled; `300` = 5-min suggested)
- [x] `"idle_since"` field in `GET /status` response (ISO8601 timestamp when unloaded, null otherwise)
- [ ] **Operator test:** set `EHC_IDLE_TIMEOUT_SECONDS=60`, wait, confirm `/system/memory` shows ~4.6 GB freed; send a request, confirm cold-start, confirm `idle_since` clears
- [x] Trade-off documented in `docs/MEMORY_RUNBOOK.md`

---

### Phase 15: Concurrency Correctness & Multiplexing Research — PARTIAL · Roy decision needed

> **Addresses:** [L2](LIMITATIONS.md#l2-single-model-residency) · **Research:** `docs/research/MLX_MULTIPLEXING_OPTIONS.md`

- [x] Fix hot-swap race condition in `ProcessManager` (`swapMu` + `mu` mutexes, commit 9ad2cbf)
- [x] Document MLX multiplexing alternatives in `docs/research/MLX_MULTIPLEXING_OPTIONS.md`
- [x] Verify upstream mlx_lm bug status (#965, #754, #883) against current pinned version
- [ ] **Roy reviews** `docs/research/MLX_MULTIPLEXING_OPTIONS.md` and decides direction
- [ ] **Implement chosen direction** (TBD pending Roy's decision)

---

### Phase 25: Structured Observability (slog) — NOT STARTED · pre-condition for Phase 24

> **Addresses:** [L7](LIMITATIONS.md#l7-lack-of-structured-observability) · **Roadmap:** [R5](ROADMAP.md#r5-structured-observability--near-term)
> **Why before Phase 24:** Request IDs are needed to correlate per-agent metrics correctly.

- [ ] Replace all `log.Printf` calls in `handler.go` and `manager.go` with `slog` (Go stdlib, zero new dependencies)
- [ ] Emit structured JSON log lines: `{"time", "level", "msg", "request_id", "agent_name", "duration_ms", "model"}`
- [ ] Add `X-Request-ID` response header (generate UUID per request if not provided by client)
- [ ] Add in-memory event ring buffer (last 200 events) on `GET /debug/events` (admin token required)
- [ ] Add structured log fields to swap events: `{"event":"swap","from_model","to_model","duration_ms","trigger":"implicit|explicit|promote"}`

---

### Phase 24: Agent Identity, Per-Client Routing & Metrics — NOT STARTED · after Phase 25

> **Addresses:** Future multi-model routing, observability, firewall interception · **Roadmap:** [R8](ROADMAP.md#r8-agent-identity-per-client-routing--firewall-interception) · **Solution:** [S16](SOLUTIONS.md#s16-agent-identity--per-client-routing-proposed--phase-24)

- [ ] **⚡ PRIORITY (no code needed) — Retrofit `X-Agent-Name` header into existing client setup guides:**
    - [ ] `docs/clients/ZEROCLAW_SETUP.md`
    - [ ] `docs/clients/OPENFANG_SETUP.md`
    - [ ] `docs/clients/OPENCLAW_SETUP.md`
    - [ ] `docs/clients/HERMES_AGENT_SETUP.md`
    - [ ] `docs/clients/OPENCODE_SETUP.md`
    - [ ] Note in each: header is required; omission will generate a `[WARN]` once Phase 24 code lands
- [ ] **`X-Agent-Name` parsing** in `HandleCompletions`:
    - [ ] Extract and log agent name on every request (using Phase 25 slog)
    - [ ] If absent: accept but emit `[WARN] missing X-Agent-Name` — not a hard error yet
- [ ] **Config-file routing table** (`config.toml` at project root):
    - [ ] Parse `[routing]` section at startup in `cmd/event-horizon/main.go`
    - [ ] `default_model` field — used when agent has no pin and request carries no `model` field
    - [ ] `[routing.pins]` map: agent slug → model HF path
    - [ ] Hot-reload on `SIGHUP` (no daemon restart needed to change pins)
- [ ] **Per-agent in-memory metrics** (`sync.Map` in `EventHorizonServer`):
    - [ ] Track: request count, tokens out, avg TTFT, last model, last seen timestamp
    - [ ] Expose on `GET /metrics/agents` (admin token required)
- [ ] **Firewall interception hook** — implement only after Shapeshifter-Airlock Phase 4 complete:
    - [ ] `routing.pins.<agent>.firewall_endpoint` — optional URL; called before proxying to MLX
    - [ ] <100ms timeout; fail-open (log warn, proxy anyway)
    - [ ] `routing.firewall_bypass = true` for development

---

## 🔴 On Hold

---

### Phase 13: Gemma 4 Native Integration — ON HOLD · waiting on mlx-lm upstream

> **Blocked:** `mlx-lm` lacks `gemma4` architecture support. Re-evaluate when `mlx-lm >= 0.32.x` and PR #1112 merged (tracked in recurring tasks above).

- [x] Confirmed `mlx-lm 0.31.x` lacks gemma4 architecture
- [x] Post-Gemma rollback complete: stable `mlx-lm==0.31.1` reinstalled, Go binary rebuilt
- [ ] Download `mlx-community/gemma-4-e4b-it-4bit` (already cached — 4.9 GB) and `mlx-community/gemma-4-26b-a4b-it-4bit` (~15.6 GB)
- [ ] Single-client benchmarking: TTFT and TPS for E4B (agent profile) and 26B MoE (firewall profile)
- [ ] Stability and VRAM profiling for both modules
- [ ] Substrate integration: verify hot-swap to new modules works cleanly

---

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

---

### Phase 14: Quality / Goodness Framework

> **Addresses:** [L7](LIMITATIONS.md#l7-lack-of-structured-observability) (partial) · **Roadmap:** R6
> **Dependency:** Meaningful goodness scoring requires Phase 25 (slog) for per-request telemetry.

- [ ] Define multi-dimensional benchmarks:
    - [ ] **Firewall profile** (Shapeshifter-Airlock): reasoning logic, prompt adherence, refusal robustness
    - [ ] **Agent profile** (Claws): tool-calling precision, JSON schema adherence, TTFT, context utilization
- [ ] Prototype "Goodness Score": aggregate TPS, TTFT, and weighted reasoning score into a single normalized value per hardware profile

---

### Phase 19: Memory Virtualization — LOW PRIORITY · partially superseded

> **Note:** KV Cache Offloading (original Phase 19 sub-task) is not applicable on Apple Silicon — "system RAM" and "VRAM" are the same physical pool. See [LIMITATIONS.md L5-B](LIMITATIONS.md#l5-vram-fragmentation). The relevant memory work is now Phase 23 (pressure monitoring) and Phase 26 (idle unloading).

- [ ] Investigate `MTLHeap`/`MTLBuffer` allocation patterns in the Metal backend — assess whether two small models (3B + 1B) can coexist in 24 GB
- [ ] ~~KV Cache Offloading~~ — **not applicable on Apple Silicon unified memory** (see L5-B)
- [ ] ~~Predictive De-fragmentation~~ — **MLX manages its own allocator; external compaction not exposed**

---

### Phase 20: Advanced Hardware Telemetry

> **Dependency:** Phase 23 (memory pressure) should land first to establish the telemetry pattern.

- [ ] Hook into SMC for real-time M5 core temperatures; auto-route to smaller model if > 95°C
- [ ] Unified telemetry API: consolidate VRAM, thermal, NPU/GPU utilisation into one endpoint

---

### Phase 21: Zero-Interruption Model Pre-warming — CONTINGENCY

> **Status:** Pursue only if Phase 16 had passed (it didn't) and LoRA multi-tenancy (E2) is insufficient. On the 24 GB M5 with ~11.6 GB of cached models and ~2 GB free RAM, running two models simultaneously is not feasible anyway — dual-model warm-up requires >9 GB headroom.
>
> **Revised cold-swap context:** E1 shows cold swaps take 1.9–3.8s (not 20-30s as previously estimated). The urgency of pre-warming is reduced accordingly.

- [ ] `POST /v1/preload` — load new model in background on a temporary port without stopping the current model
    - VRAM budget check: reject if model A + model B > 22 GB
    - Returns `202 Accepted` immediately; poll `GET /v1/preload/status` for readiness
- [ ] Atomic port cutover once warm model is healthy; drain in-flight requests (2s grace period)
- [ ] `GET /status` update to report warming model alongside active model

---

## ✅ Complete

---

### Phase 18: External Orchestration API ✅ COMPLETE (2026-04-06)

> All endpoints implemented in `handler.go`. Admin token auth on all `/system/*` routes.

- [x] `POST /system/maintenance` — sets maintenance flag; in-flight requests drain (10s)
- [x] `POST /system/maintenance/release` — clears flag; optional `promote_model`
- [x] `GET /system/maintenance/status` — poll state
- [x] `POST /v1/model/swap` — explicit swap; 409 on contention
- [x] `GET /metrics` — MLX Metal telemetry; TTL-cached 5s
- [x] `X-EHC-Admin-Token` auth on all admin endpoints
- [x] `GET /status` updated with maintenance fields
- [x] Integration test: full proving-ground cycle verified

---

### Phase 17: Production Correctness Fixes ✅ COMPLETE (2026-04-06)

> All fixes in `handler.go` and `manager.go`. **Operator verification still outstanding** — see checklist below.

- [x] SSE-aware streaming proxy: `bufio.ReadBytes('\n')` + `http.Flusher.Flush()`
- [x] `/metrics` TTL cache: 5s; one subprocess spawn per monitoring interval
- [x] Maintenance drain race: atomic `inFlightCount`; polls to zero before proceeding
- [x] `/v1/model/swap` 409 on contention: `TrySwitchModel()` + `ErrSwapInProgress`

**Operator verification checklist (COMPLETE 2026-04-07):**
- [x] Streaming: `verify_streaming.py` — tokens arrive incrementally
- [x] Metrics rate: `verify_metrics_ttl.py` — one subprocess spawn per 5s
- [x] Drain: `verify_drain.py` — completion finishes before maintenance proceeds

---

### Phases 1–12 ✅ COMPLETE (archived)

<details>
<summary>Click to expand</summary>

| Phase | Title | Key Outcome |
|:------|:------|:------------|
| 1 | Environment & Setup | `uv` transition, OpenRouter activation |
| 2 | Performance & Connectivity | VRAM guard (22 GB), CLI help |
| 3 | Concurrency Torture Testing | MLX stable at 2 concurrent |
| 4 | Orchestration & Resource Optimization | Pivoted to `mlx_lm.server` as primary |
| 5 | Native Architecture Integration | `RemoteNativeProvider` wrapping `mlx_lm.server` |
| 6 | Substrate Streamlining | Removed Llama.cpp and Ollama |
| 7 | Go Substrate Migration | Zero-dependency Go daemon on port 8000 |
| 8 | Acceptance Criteria & Test Plan | 50+ concurrent stress tests; zombie recovery |
| 9 | Python Eradication | Deleted orchestrator.py, providers/, pruned deps |
| 10 | Local-Only Simplification | Removed OpenRouter; local-only architecture |
| 11 | Hardware Performance & SLO Verification | 0.74s P95 TTFT; SLOs documented |
| 12 | LLM Candidate Evaluation | Hermes-3-8B-4bit selected as Apex Archetype |

**Phase 12 key finding:** On 24 GB M5, multi-agent workloads are limited to the 8B parameter tier. Hermes-3-Llama-3.1-8B-4bit is the only tested model maintaining double-digit TPS under 5-client pressure.

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
| `Mistral-Nemo-Instruct-2407-4bit` | — | **Removed 2026-04-07** | No assigned role; freed 6.4 GB |
| `Qwen2.5-32B-Instruct-4bit` | — | **Removed 2026-04-07** | OOMs on 24 GB M5; freed 17 GB |
| `gemma-2-27b-it-4bit` | — | **Removed 2026-04-07** | No active role; freed 14 GB |
| `Qwen2.5-Coder-32B-Instruct-4bit` | — | **Removed 2026-04-05** | OOMs during generation |
| `gemma-4-26b-a4b-it-4bit` | — | **Removed 2026-04-05** | mlx-lm unsupported; re-download when >= 0.32.x |

**Pending downloads (do not download without Roy approval):**
- `mlx-community/Qwen2.5-Coder-14B-Instruct-4bit` (~8.8 GB) — ZeroClaw coding model candidate
- `mlx-community/gemma-4-26b-a4b-it-4bit` (~15.6 GB) — re-download when mlx-lm >= 0.32.x + PR #1112 merged
