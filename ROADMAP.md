# EHC Roadmap

> **Purpose:** Directional document. Records where Event Horizon Core is heading,
> what bets we're placing, and why. Updated when we **decide** something.
>
> **Cross-references:** [LIMITATIONS.md](LIMITATIONS.md) (diagnosis) · [TASKS.md](TASKS.md) (execution) · [REVIEW_04_06.md](REVIEW_04_06.md) (discussion) · [SOLUTIONS.md](SOLUTIONS.md) (how)

---

## Current Architecture (April 2026)

```
┌─────────────────────────────────────────────┐
│  Claw Fleet (ZeroClaw, OpenFang, Hermes...) │
│              HTTP :8000                     │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         Go Orchestrator (EHC)               │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ HTTP Proxy   │  │ Maintenance API      │  │
│  │ /v1/chat/*   │  │ /system/maintenance  │  │
│  │ SSE-aware ✓  │  │ /v1/model/swap       │  │
│  └──────┬──────┘  │ /metrics (TTL cache) │  │
│         │         └──────────────────────┘  │
│  ┌──────▼──────┐                            │
│  │ Supervisor  │  (ProcessManager)          │
│  │ os/exec     │  SIGKILL + health poll     │
│  │ In-flight   │  drain on maintenance ✓    │
│  └──────┬──────┘                            │
└─────────┼───────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────┐
│    mlx_lm.server (Python/MLX)               │
│    Port 8080 · Metal · Prefix Caching       │
│    uv-managed · Single model resident       │
└─────────────────────────────────────────────┘
```

**Default model:** Hermes-3-Llama-3.1-8B-4bit (4.2 GB)  
**Hardware:** Apple M5, 24 GB unified memory (22 GB usable guardrail)

---

## Strategic Principles

1. **Measure before migrating.** No architectural rewrite without empirical evidence that it solves the measured bottleneck. (See [LIMITATIONS.md Experiment E1](LIMITATIONS.md#e1-cold-start-breakdown-measurement))
2. **Go stays as orchestrator.** The Go layer's value (process management, concurrency, maintenance API, auth) is proven. Backend changes happen *underneath* it.
3. **Experiments over assumptions.** Use EHC's own maintenance mode as a self-testing harness to evaluate candidate solutions before committing.
4. **Near-term horizon (6-12 months).** Design for the next hardware upgrade (M6, likely 48GB+), efficiency improvements in models, and maturation of off-the-shelf libraries.

---

## Roadmap Items

### R1: Fix Immediate Production Issues ✅ COMPLETE (2026-04-06)

> **Limitations addressed:** [L3](LIMITATIONS.md#l3-metrics-subprocess-overhead) · [L4](LIMITATIONS.md#l4-streaming-proxy-buffering) · [L8](LIMITATIONS.md#l8-maintenance-drain-race) · [L9](LIMITATIONS.md#l9-v1modelswap-blocked-on-in-progress-swaps)

| Item | Status |
|:-----|:-------|
| Cache `/metrics` output with 5s TTL | ✅ Done — `metricsCache` in `handler.go` |
| SSE-aware streaming proxy (Phase 17) | ✅ Done — `bufio.ReadBytes` + `http.Flusher` |
| Maintenance drain race (in-flight tracking) | ✅ Done — atomic `inFlightCount` + 10s drain |
| `/v1/model/swap` returns 409 on contention | ✅ Done — `TrySwitchModel()` + `ErrSwapInProgress` |

---

### R2: Measure the Cold-Start Bottleneck ⏱️ NEXT

> **Limitations addressed:** [L1](LIMITATIONS.md#l1-cold-start-model-swap-latency)  
> **Experiment:** [E1](LIMITATIONS.md#e1-cold-start-breakdown-measurement)

Before investing in MLX-Swift (Phase 16), instrument `manager.go` to measure the actual time breakdown of a model swap. This determines whether the highest-leverage fix is:

- **If Python overhead > 30%:** MLX-Swift migration has high value → proceed to R4
- **If weight loading > 85%:** Language doesn't matter → pivot to mmap persistence or pre-warming
- **If health polling > 20%:** Reduce poll interval from 500ms to 100ms (trivial fix)

---

### R3: Explore LoRA Multi-Tenancy ⏱️ NEAR-TERM

> **Limitations addressed:** [L1](LIMITATIONS.md#l1-cold-start-model-swap-latency) · [L2](LIMITATIONS.md#l2-single-model-residency)  
> **Experiment:** [E2](LIMITATIONS.md#e2-lora-multi-tenancy-pilot)

This is potentially the highest-leverage, lowest-risk path to multi-model serving:

1. **`llm-factory`** trains a coding LoRA on Hermes-3-8B
2. **`llm-proving-ground`** benchmarks it against Qwen2.5-Coder-14B
3. If quality is within 10%: adopt as primary multi-model strategy
4. If not: continue with model-swapping approach

**Why this matters:** If LoRA multi-tenancy works, it makes R4 (Swift migration) *less urgent* — you get sub-second "model switching" without changing the language layer at all. This path is available today; Swift requires months of additional ecosystem maturity.

---

### R4: MLX-Swift Spike (48 Hours) ⏱️ AFTER R2 — GATED

> **Limitations addressed:** [L1](LIMITATIONS.md#l1-cold-start-model-swap-latency) · [L6](LIMITATIONS.md#l6-python-dependency)  
> **Experiment:** [E3](LIMITATIONS.md#e3-mlx-swift-48-hour-spike)  
> **TASKS:** Phase 16

#### Is MLX-Swift the right architectural direction?

**Short answer:** Desirable end-state. Not ready for prime time today. Gate it carefully.

**The case for MLX-Swift (eventually):**
- Eliminates the Python/`uv` dependency chain entirely — a broken venv can no longer take the station offline
- In-process model management means no SIGKILL/restart cycle, potentially enabling true multi-model residency within a single Swift process
- Native Swift on Apple Silicon is Apple's stated direction for Metal compute
- Long-term, Swift actors + structured concurrency may provide cleaner multi-model memory management than Go→Python IPC

**The case against committing now:**
- **Ecosystem gap.** As of April 2026, `MLX-Swift` is focused on training and batch inference, not production serving. Features we rely on daily — HTTP server, continuous batching, prefix caching, SSE streaming, LoRA adapters — are all absent or immature in Swift. `mlx_lm.server` has years of serving-oriented development that MLX-Swift doesn't replicate yet.
- **Wrong bottleneck.** The dominant cold-start cost is weight loading (~15-25s), which is language-independent. Rewriting in Swift eliminates ~2-4s of Python startup but leaves the 15-25s wall unchanged. If weight loading is >85% of swap time (E1 will tell us), Swift migration reduces total swap time by <15%.
- **Reimplementation cost.** Building a production Swift inference server with prefix caching, SSE, LoRA, quantization, and health-check APIs is 2-4 months of work — all replacing things `mlx_lm.server` already provides.
- **Architecture clarity.** The Go orchestrator's value is independent of the inference backend. "Replace Go with Swift-NIO" is a separate, higher-risk decision from "use Swift for inference." Keep these separate.

**The right approach:**
- Do not commit to Phase 16 without E1 data and E3 spike results
- If E1 shows Python overhead >30% AND E3 spike TTFT <2s → full Phase 16 greenlit
- If weight loading dominates → pursue S3 (mmap) or S2 (pre-warming) instead
- Verify the MLX-Swift ecosystem checklist in [S1](SOLUTIONS.md#s1-mlx-swift-native-inference-library-proposed--gated) before committing any engineering resources

**Target architecture if greenlit:**
```
Go Orchestrator → Unix Socket → Swift Inference Library
```
Not "replace Go with Swift." Go keeps orchestration. Swift does inference.

**Time-boxed investigation:**
- Build the absolute minimum Swift binary: load Hermes-3-8B, generate one completion
- Measure TTFT from process start to first token
- Compare against `uv run mlx_lm.server`

**Go/No-Go criteria (committed before starting):**
- If Swift TTFT < 2s → Full Phase 16 greenlit
- If Swift TTFT > 10s → Pivot to mmap/pre-warming approaches
- If prefix caching isn't available in MLX-Swift → Assess reimplementation cost vs. benefit before proceeding

---

### R5: Structured Observability ⏱️ NEAR-TERM

> **Limitations addressed:** [L7](LIMITATIONS.md#l7-lack-of-structured-observability)

Upgrade from `log.Printf` to `slog` (Go stdlib structured logging). Add:
- Request ID per inference call
- Agent identification (`X-Agent-Name` header)
- Swap event structured logs (model, duration, trigger)
- In-memory event ring buffer on `/debug/events`

Low effort, high diagnostic value as the claw fleet scales.

---

### R6: VRAM Optimization & Thermal Safety ⏱️ LATER

> **Limitations addressed:** [L5](LIMITATIONS.md#l5-vram-fragmentation)  
> **TASKS:** Phase 19 (Memory Virtualization), Phase 20 (Telemetry)

Deferred until:
- R2 provides cold-start measurements
- R3 determines if LoRA multi-tenancy reduces VRAM pressure
- Hardware upgrade (M6) may make aggressive VRAM optimization unnecessary

**Thermal recommendation:** Rate-limiting and concurrency throttling are safer thermal defenses than model-swapping under heat. Model swaps are themselves memory-bandwidth-intensive and spike temperature further. If the M5 is overheating, serialize requests or inject micro-sleeps between generation batches rather than triggering a swap.

---

### R7: Python Pre-warming (Contingency) ⏱️ IF NEEDED

> **Limitations addressed:** [L1](LIMITATIONS.md#l1-cold-start-model-swap-latency)  
> **TASKS:** Phase 21

Only pursue if:
- R4 (Swift spike) fails or is deferred
- R3 (LoRA) doesn't provide sufficient model diversity
- Cold-start latency remains the primary pain point

This is the "known solution" — dual Python processes, atomic port swap. It works but adds VRAM pressure and process management complexity.

---

## Decision Log

| Date | Decision | Rationale | Ref |
|:-----|:---------|:----------|:----|
| 2026-04-06 | Fix production bugs before any architectural migration | SSE streaming, metrics churn, drain race, 409 contention — all fixed. These are cheaper than any rewrite and remove known failure modes. | R1 |
| 2026-04-06 | Gate MLX-Swift behind E1 measurement and 48h spike | Avoid multi-week investment without empirical evidence. Weight loading is language-independent; Python overhead may be <15% of total swap time. | [REVIEW_04_06.md](REVIEW_04_06.md) LLM3, R4 |
| 2026-04-06 | Keep Go as orchestrator regardless of inference backend | Proven battle-tested code; Swift-NIO rewrite is high risk with no benefit over Go for orchestration. Backend changes happen underneath the Go layer. | [REVIEW_04_06.md](REVIEW_04_06.md) LLM3 |
| 2026-04-06 | Explore LoRA multi-tenancy before committing to Swift | Higher leverage, lower risk: works today with mlx-lm, tested via llm-factory + llm-proving-ground. If LoRA works, Swift migration becomes less urgent. | R3, [REVIEW_04_06.md](REVIEW_04_06.md) LLM2, LLM3 |
| 2026-04-06 | Prioritize MLX-Swift investigation over Python pre-warming (if gated) | Swift solves cold-start + Python dependency simultaneously; pre-warming only solves cold-start | [REVIEW_04_06.md](REVIEW_04_06.md) LLM2 |
| 2026-04-01 | Go + MLX-LM hybrid as stable foundation | Best balance of process safety and inference performance | [SYNC_LOG.md](SYNC_LOG.md) |
| 2026-03-31 | Retire Python orchestration layer | Go provides superior process supervision and concurrent HTTP handling | [SYNC_LOG.md](SYNC_LOG.md) |
| 2026-03-31 | Remove Ollama and Llama.cpp backends | MLX-only reduces attack surface and memory overhead | [SYNC_LOG.md](SYNC_LOG.md) |
