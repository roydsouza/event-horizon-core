# EHC Limitations & Strategic Risk Register

> **Purpose:** Diagnostic document. Lists what constrains Event Horizon Core today
> and what external risks could change our trajectory. Each limitation includes
> candidate solutions with honest pros/cons. Updated when we **discover** something new.
>
> **Cross-references:** [ROADMAP.md](ROADMAP.md) (decisions) · [TASKS.md](TASKS.md) (execution)

---

## Engineering Limitations

> Ordered by **severity × leverage** — what hurts most today and unlocks the most value if solved.

---

### L1: Cold-Start Model Swap Latency ⬆️ CRITICAL

**Current state:** Hot-swapping models kills the running `mlx_lm.server` process (SIGKILL to entire process group), spawns a new Python interpreter via `uv`, loads weights from disk into Metal unified memory, and polls `/health` until ready. Total: **20-30 seconds** of complete inference unavailability.

**Impact:** Every active agent gets a 503 during swaps. As the claw fleet grows, a single operator-initiated swap disrupts all sessions simultaneously.

**Root cause breakdown (estimated, needs measurement — see Experiment E1):**
| Component | Estimated Time | Language-dependent? |
|:----------|:---------------|:--------------------|
| SIGKILL + process teardown | ~1s | No |
| `uv` environment resolution | ~1-2s | Python-specific |
| Python interpreter startup | ~1s | Python-specific |
| Model weight loading (SSD → Metal) | **~15-25s** | **No** |
| Health check polling (500ms intervals) | ~1-3s | No |

> [!WARNING]
> The dominant cost is **weight loading**, which is language-independent. Rewriting in Swift eliminates ~2-4s of Python overhead but does not address the 15-25s core bottleneck.

#### Candidate Solutions

**A. MLX-Swift Native Server** → ROADMAP R2, TASKS Phase 16
| | |
|:--|:--|
| **Approach** | Replace `uv run mlx_lm.server` with a compiled Swift binary using MLX-Swift |
| **Pros** | Eliminates Python entirely (~2-4s savings); enables in-process model management (no SIGKILL cycle); potential for thread-level multi-model residency |
| **Cons** | MLX-Swift serving ecosystem is immature; prefix caching and speculative decoding may need reimplementation; significant engineering effort (2-3 weeks) |
| **Go/No-Go** | Run Experiment E1 first — if weight loading dominates, Swift saves <15% of total swap time |

**B. Python Pre-warming (Dual-Process)** → TASKS Phase 21
| | |
|:--|:--|
| **Approach** | Start a second `mlx_lm.server` on a temporary port while the current one serves; atomic port swap on readiness |
| **Pros** | Zero-downtime swaps; works today with existing Python stack; no new language to maintain |
| **Cons** | Requires 2x VRAM during warm-up window (only feasible for small models); adds process management complexity; doesn't solve Python dependency |
| **Go/No-Go** | Only viable if combined model weights < 18GB (strict VRAM budget) |

**C. Memory-Mapped Weight Persistence** → No phase assigned
| | |
|:--|:--|
| **Approach** | Keep model weights memory-mapped even when the inference server is stopped; new process re-attaches to existing mappings |
| **Pros** | Near-instant "warm restart" (~1-2s total); no language migration needed; works with current architecture |
| **Cons** | Requires changes to `mlx_lm.server` internals or upstream contribution; macOS unified memory complicates mmap semantics; risk of stale mappings |
| **Go/No-Go** | Investigate whether MLX's `mx.load()` supports mmap mode for safetensors |

**D. LoRA-Based Multi-Tenancy** → ROADMAP R3
| | |
|:--|:--|
| **Approach** | Standardize on one base model; swap only LoRA adapters (~100MB each) instead of full model weights |
| **Pros** | Adapter swaps take <1s; all "models" share VRAM for base weights; works today with `mlx-lm` LoRA support |
| **Cons** | Requires training task-specific LoRAs (weeks of `llm-factory` work); LoRA quality may not match purpose-built models; limits model diversity |
| **Go/No-Go** | Train one pilot LoRA, benchmark against purpose-built model in `llm-proving-ground` |

---

### L2: Single-Model Residency ⬆️ HIGH

**Current state:** Only one model can be loaded in VRAM at a time. Serving a different model means fully unloading the current one.

**Impact:** Prevents simultaneous specialized inference (e.g., coding model for ZeroClaw + reasoning model for HermesAgent). Forces all agents onto the same model or suffers 20-30s swap penalties.

#### Candidate Solutions

**A. LoRA Multi-Tenancy** (same as L1-D above)
| | |
|:--|:--|
| **Pros** | Multiple "models" resident simultaneously; 4.6GB total for base + 4 adapters |
| **Cons** | All agents constrained to same base architecture |

**B. Small Model Pool** → No phase assigned
| | |
|:--|:--|
| **Approach** | Run multiple `mlx_lm.server` instances on different ports, each with a small model (1B, 3B) |
| **Pros** | True multi-model; 1B + 3B + 8B = ~10GB, fits easily in 24GB |
| **Cons** | KV cache memory grows per-instance; requires intelligent routing in Go layer; port management complexity |

**C. MLX-Swift In-Process Multi-Model** → TASKS Phase 16 (if spike succeeds)
| | |
|:--|:--|
| **Approach** | Load multiple models as Swift objects in a single process, sharing the Metal device |
| **Pros** | Maximum control over memory layout; no IPC overhead |
| **Cons** | Requires Swift migration; MLX-Swift multi-model support unproven; risk of Metal resource contention |

---

### L3: `/metrics` Subprocess Overhead ⬆️ HIGH

**Current state:** `GET /metrics` shells out to `uv run python -c "import mlx.core..."` on every call, spawning an entire Python interpreter to read two integers.

**Impact:** Continuous subprocess churn under monitoring; ~1-2s latency per metrics call; fails silently if `uv` environment is broken.

#### Candidate Solutions

**A. TTL Cache in Go** → No phase assigned (immediate fix)
| | |
|:--|:--|
| **Approach** | Cache metrics output for 5 seconds; serve from cache on subsequent requests |
| **Pros** | Trivial to implement (< 30 lines of Go); eliminates subprocess churn |
| **Cons** | Metrics lag by up to 5s; doesn't eliminate Python dependency for metrics |

**B. Read from macOS System APIs** → No phase assigned
| | |
|:--|:--|
| **Approach** | Use `ioreg` or `sysctl` to read GPU memory stats directly from Go |
| **Pros** | Zero Python dependency; real-time readings |
| **Cons** | May not provide MLX-specific metrics (active vs. peak); less accurate |

**C. Expose via Supervised Server** → No phase assigned
| | |
|:--|:--|
| **Approach** | Request `mlx_lm.server` upstream add a `/metrics` endpoint (or use its existing capabilities) |
| **Pros** | In-process, zero overhead; accurate MLX-specific readings |
| **Cons** | Depends on upstream accepting the contribution; may not exist yet |

---

### L4: Streaming Proxy Buffering ⬆️ MEDIUM

**Current state:** `HandleCompletions` uses `io.Copy(w, resp.Body)` which buffers SSE chunks in a 32KB buffer before flushing.

**Impact:** OpenFang's streaming mode delivers tokens in batches rather than incrementally. TTFT appears as full generation time.

**Phase:** TASKS Phase 17

#### Candidate Solutions

**A. Line-Buffered Flusher** → TASKS Phase 17
| | |
|:--|:--|
| **Approach** | Cast `ResponseWriter` to `http.Flusher`; flush after every `\n\n` boundary |
| **Pros** | ~20 lines of Go; preserves non-streaming path; matches direct-to-MLX TTFT |
| **Cons** | None significant — this is a clear bug fix |

---

### L5: VRAM Fragmentation ⬆️ MEDIUM

**Current state:** All-or-nothing VRAM usage. No ability to carve memory for multiple concurrent workloads.

**Impact:** 24GB M5 can only serve one large model; no graceful degradation under memory pressure.

#### Candidate Solutions

**A. VRAM Budget Checks** → TASKS Phase 21
| | |
|:--|:--|
| **Pros** | Prevents OOM by rejecting unsafe preloads |
| **Cons** | Reactive, not proactive; doesn't improve utilization |

**B. KV Cache Offloading** → TASKS Phase 19
| | |
|:--|:--|
| **Approach** | Swap inactive KV caches to system RAM |
| **Pros** | Frees VRAM for active generation without unloading models |
| **Cons** | Apple unified memory means "system RAM" and "VRAM" are the same physical resource; benefit is unclear on Apple Silicon |

**C. Predictive Compaction** → TASKS Phase 19
| | |
|:--|:--|
| **Approach** | Trigger memory compaction before high-load bursts |
| **Pros** | Proactive rather than reactive |
| **Cons** | Requires predicting load patterns; may cause latency spikes during compaction |

---

### L6: Python Dependency ⬆️ MEDIUM

**Current state:** Go daemon's health depends on `uv`, Python venv, and `mlx-lm` package stability. A broken venv = dead inference.

**Impact:** Fragile deployment; `uv sync` failures or `mlx-lm` breaking changes can take the entire station offline.

#### Candidate Solutions

**A. MLX-Swift Migration** → TASKS Phase 16
| | |
|:--|:--|
| **Pros** | Eliminates Python entirely |
| **Cons** | See L1 risks above |

**B. Containerized Python** → No phase assigned
| | |
|:--|:--|
| **Approach** | Pin `mlx-lm` and dependencies in a container or frozen venv |
| **Pros** | Python dependency becomes hermetic; immune to upstream breakage |
| **Cons** | Metal GPU passthrough in containers is non-trivial on macOS; adds deployment complexity |

**C. Pinned `uv.lock` + CI Validation** → No phase assigned (immediate fix)
| | |
|:--|:--|
| **Approach** | Lock `uv.lock` and add CI that validates the venv builds cleanly on each commit |
| **Pros** | Catches breakage early; trivial to implement |
| **Cons** | Doesn't prevent runtime failures; still dependent on upstream |

---

### L7: Lack of Structured Observability ⬆️ LOW (but grows with scale)

**Current state:** All logging via `log.Printf`. No request tracing, no structured events, no VRAM utilization history.

**Impact:** Debugging "why did my agent get a 503" requires reading raw logs. No ability to correlate swap events with agent failures.

#### Candidate Solutions

**A. Structured JSON Logging** → No phase assigned
| | |
|:--|:--|
| **Approach** | Replace `log.Printf` with `slog` (Go stdlib); emit JSON log lines with request ID, agent name, duration |
| **Pros** | Stdlib, zero dependencies; parseable by any log tool |
| **Cons** | Requires touching every log call site |

**B. Lightweight Metrics Emitter** → No phase assigned
| | |
|:--|:--|
| **Approach** | In-memory ring buffer of recent events (swaps, 503s, VRAM readings); exposed via `/debug/events` |
| **Pros** | Self-contained; no external dependencies; useful for debugging |
| **Cons** | Not a full observability solution; data lost on restart |

---

## Strategic Risks

> External factors outside our direct control that could change EHC's trajectory.
> Each risk includes a **contingency plan** — what we'd do if it materializes.

---

### R1: Apple MLX Roadmap Uncertainty

**Risk:** Apple could shift MLX focus to on-device inference for iOS/iPadOS, deprioritizing macOS server-side features (continuous batching, prefix caching, multi-model serving).

**Probability:** Medium — Apple's track record suggests consumer-device bias.

**Contingency:** If MLX stagnates for server workloads, evaluate `vllm-mlx` (Metal fork of vLLM) or `llama.cpp` Metal backend as drop-in replacements. The Go orchestrator's proxy architecture makes backend swaps relatively painless.

---

### R2: `mlx-lm` Upstream Breaking Changes

**Risk:** We're pinned to `mlx-lm 0.31.1`. Upstream releases could break our venv, change API surfaces, or introduce regressions (e.g., the Gemma 4 architecture gap).

**Probability:** High — already experienced with Gemma 4 (Phase 13).

**Contingency:** Maintain strict `uv.lock` pinning. Test new releases in a `llm-proving-ground` dry-run before upgrading production. Keep Phase 13-style rollback procedures documented.

---

### R3: Hardware Evolution (M6/M7)

**Risk:** An M6 with 48GB+ unified memory could make current VRAM optimization work (fragmentation control, aggressive budgeting) unnecessary. Conversely, new hardware could introduce architectural changes that break our Metal assumptions.

**Probability:** High (hardware upgrade is planned).

**Contingency:** Design EHC with configurable VRAM budgets (not hardcoded 22GB). When new hardware arrives, re-run `llm-proving-ground` benchmarks to recalibrate SLOs. The Go orchestrator's hardware abstraction makes this a configuration change, not a code change.

---

### R4: Off-the-Shelf Orchestrators Mature

**Risk:** Projects like `vllm-mlx`, `ollama` (Metal), or Apple's own inference frameworks could provide turn-key solutions that make EHC's custom orchestration redundant.

**Probability:** Medium — the Apple Silicon local inference ecosystem is rapidly evolving.

**Contingency:** EHC's value-add is the maintenance API, multi-agent coordination, and integration with `llm-factory`/`llm-proving-ground`. If a better inference backend appears, adopt it *underneath* the Go orchestrator rather than replacing EHC entirely. The proxy architecture was designed for exactly this kind of backend swap.

---

### R5: Model Efficiency Improvements

**Risk:** Future models (Gemma 5, Llama 5) may be dramatically more efficient — running 32B-equivalent quality at 8B-equivalent compute. This would make multi-model VRAM optimization less critical, but would also raise the bar for what "good enough" local inference means.

**Probability:** High — model efficiency is improving rapidly.

**Contingency:** This is a *positive* risk. More efficient models mean more headroom for multi-model residency and lower swap costs. The key is to keep the `llm-proving-ground` benchmark suite current so we can quickly evaluate new models against our SLOs.

---

### R6: LoRA Quality Gap

**Risk:** Task-specific LoRAs may not match the quality of purpose-built models fine-tuned for specific agent roles.

**Probability:** Medium — depends heavily on base model capability and LoRA rank.

**Contingency:** Run a structured experiment via `llm-proving-ground`: train a coding LoRA on Hermes-3-8B, benchmark it against a purpose-built coding model (e.g., Qwen2.5-Coder-14B). If the quality gap is >5% on coding benchmarks, the multi-tenancy strategy needs to shift to small purpose-built models rather than LoRA adapters.

---

## Experiments

> Experiments to run using EHC's maintenance mode as a self-testing harness.
> Each experiment has clear go/no-go criteria.

### E1: Cold-Start Breakdown Measurement

**Goal:** Determine the actual time breakdown of a model swap to prioritize optimization efforts.

**Method:**
1. Enter maintenance mode
2. Instrument `manager.go`: add `time.Now()` checkpoints at each stage (SIGKILL → process exit confirmed → `uv` start → Python ready → weight loading start → weight loading end → health OK)
3. Swap between Hermes-3-8B and Llama-3.2-3B three times each direction
4. Record all timings

**Go/No-Go for MLX-Swift:** If Python startup + `uv` overhead is >30% of total swap time → Swift migration has high leverage. If <15% → optimize the weight loading path instead.

### E2: LoRA Multi-Tenancy Pilot

**Goal:** Determine if LoRA adapters can provide agent-specialized inference without model swaps.

**Method:**
1. Train a coding-focused LoRA on Hermes-3-8B using `llm-factory`
2. Evaluate on coding benchmarks via `llm-proving-ground`
3. Compare against Qwen2.5-Coder-14B (purpose-built coding model)

**Go/No-Go:** If LoRA scores within 10% of Qwen2.5-Coder-14B on HumanEval → adopt LoRA multi-tenancy as primary strategy.

### E3: MLX-Swift 48-Hour Spike

**Goal:** Determine if MLX-Swift can serve inference with significantly lower cold-start than Python.

**Method:**
1. Build minimal Swift binary: load Hermes-3-8B, generate one completion
2. Measure TTFT from binary execution to first token
3. Compare against `uv run mlx_lm.server` TTFT

**Go/No-Go:** If Swift TTFT is <2s (vs. current ~20-30s) → continue full Phase 16. If >10s → the bottleneck is weight loading, not Python, and Swift migration has limited value.
