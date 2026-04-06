# EHC Roadmap

> **Purpose:** Directional document. Records where Event Horizon Core is heading,
> what bets we're placing, and why. Updated when we **decide** something.
>
> **Cross-references:** [LIMITATIONS.md](LIMITATIONS.md) (diagnosis) · [TASKS.md](TASKS.md) (execution) · [REVIEW_04_06.md](REVIEW_04_06.md) (discussion)

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
│  └──────┬──────┘  │ /v1/model/swap       │  │
│         │         │ /metrics             │  │
│         │         └──────────────────────┘  │
│  ┌──────▼──────┐                            │
│  │ Supervisor  │  (ProcessManager)          │
│  │ os/exec     │  SIGKILL + health poll     │
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

### R1: Fix Immediate Production Issues ⏱️ NOW

> **Limitations addressed:** [L3](LIMITATIONS.md#l3-metrics-subprocess-overhead) · [L4](LIMITATIONS.md#l4-streaming-proxy-buffering)

| Item | Effort | Impact |
|:-----|:-------|:-------|
| Cache `/metrics` output with 5s TTL | 1 hour | Eliminates subprocess churn |
| SSE-aware streaming proxy (Phase 17) | 2 hours | Fixes OpenFang TTFT reporting |

These are clear bug fixes with no architectural risk. Do them first.

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

**Why this matters:** If LoRA multi-tenancy works, it makes R4 (Swift migration) *less urgent* — you get sub-second "model switching" without changing the language layer at all.

---

### R4: MLX-Swift Spike (48 Hours) ⏱️ AFTER R2

> **Limitations addressed:** [L1](LIMITATIONS.md#l1-cold-start-model-swap-latency) · [L6](LIMITATIONS.md#l6-python-dependency)  
> **Experiment:** [E3](LIMITATIONS.md#e3-mlx-swift-48-hour-spike)  
> **TASKS:** Phase 16

Time-boxed investigation. Build the absolute minimum:
- Swift binary that loads Hermes-3-8B and generates one completion
- Measure TTFT from process start to first token
- Compare against `uv run mlx_lm.server`

**Go/No-Go criteria** (committed before starting):
- If Swift TTFT < 2s → Full Phase 16 greenlit
- If Swift TTFT > 10s → Pivot to mmap/pre-warming approaches
- If prefix caching isn't available in MLX-Swift → Assess reimplementation cost vs. benefit

**If greenlit, target architecture:**
```
Go Orchestrator → Unix Socket → Swift Inference Library
```
Not "replace Go with Swift." Go keeps orchestration. Swift does inference.

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

**Thermal recommendation (from LLM2 + LLM3 review):** Rate-limiting and concurrency throttling are safer thermal defenses than model-swapping under heat. Don't swap models in response to high temperatures — that causes more memory bandwidth heat, not less.

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
| 2026-04-06 | Prioritize MLX-Swift investigation over Python pre-warming | Swift solves cold-start + Python dependency simultaneously | [REVIEW_04_06.md](REVIEW_04_06.md) LLM2 |
| 2026-04-06 | Add 48-hour spike gate before full Swift commitment | Avoid multi-week investment without empirical evidence | [REVIEW_04_06.md](REVIEW_04_06.md) LLM3 |
| 2026-04-06 | Keep Go as orchestrator regardless of inference backend | Proven battle-tested code; Swift-NIO rewrite is high risk | [REVIEW_04_06.md](REVIEW_04_06.md) LLM3 |
| 2026-04-06 | Explore LoRA multi-tenancy as alternative to memory virtualization | Higher leverage, lower risk than MTLHeap surgery | [REVIEW_04_06.md](REVIEW_04_06.md) LLM2, LLM3 |
| 2026-04-01 | Go + MLX-LM hybrid as stable foundation | Best balance of process safety and inference performance | [SYNC_LOG.md](SYNC_LOG.md) |
| 2026-03-31 | Retire Python orchestration layer | Go provides superior process supervision and concurrent HTTP handling | [SYNC_LOG.md](SYNC_LOG.md) |
| 2026-03-31 | Remove Ollama and Llama.cpp backends | MLX-only reduces attack surface and memory overhead | [SYNC_LOG.md](SYNC_LOG.md) |
