# Technical Review: event-horizon-core
**Date:** April 6, 2026  
**Status:** Phase 18 Complete (External Orchestration API Live)

## (a) System Architecture & Workflow

`event-horizon-core` (EHC) serves as the **low-latency inference substrate** for the AntiGravity station. It is a hybrid Go/Python system optimized specifically for Apple Silicon (M5).

### Core Components:
1.  **Orchestration Layer (Go)**:
    *   **HTTP Server**: Listens on port `8000`. Acts as a smart proxy and management interface.
    *   **Supervisor (`ProcessManager`)**: Manages the lifecycle of the underlying Python inference engine. It handles starting, stopping, health monitoring, and "Hot-Swapping" models.
    *   **Maintenance API (Phase 18)**: Provides exclusive locking (`/system/maintenance`) and model promotion logic, ensuring that heavy tasks like LLM-Factory training or Proving-Ground evals don't collide.

2.  **Inference Engine (Python/MLX)**:
    *   **`mlx_lm.server`**: Effectively the "engine room." Runs on port `8080` (supervised by Go).
    *   **`uv` Managed**: Uses `uv` for high-performance dependency management and execution.
    *   **Metal Optimization**: Hardcoded optimizations for M5, including prefix caching (`--prompt-cache-size 2048`) and speculative decoding support.

---

## (b) Pros and Cons

### Pros:
*   **M5 Native Performance**: By using `mlx-lm` directly, EHC leverages Apple's unified memory and Metal performance better than generic wrappers like Llama.cpp.
*   **Memory Safety**: The Phase 18 Maintenance API prevents OOM (Out of Memory) crashes by ensuring only one resource-heavy agent (Factory or Proving Ground) has control of the VRAM at once.
*   **Language Hybridization**: Uses Go for robust process supervision/concurrency and Python for the ML-heavy lifting—getting the best of both worlds.
*   **Hot-Swapping**: Enables a single-GPU machine (M5 laptop) to act like a multi-model cluster by swapping models on-demand in <10 seconds.

### Cons:
*   **Swap Latency**: Model swaps introduced a "cold start" penalty for the first request.
*   **VRAM Fragmentation**: Lacks granular VRAM carving (all-or-nothing approach).
*   **Python Dependency**: The Go daemon's health is tied to the stability of the Python subprocess environment.

---

## (c) Candidate Enhancements

1.  **Granular Telemetry**: Add `ThermalThrottleState` and `MemoryPressure` to `/metrics` so agents can react to heat.
2.  **Prioritized Queuing**: Implement a priority queue to favor "Interactive" (User) requests.
3.  **Layer-Persistent Swapping**: Speed up swaps between versions of the same base model by keeping shared weights resident.
4.  **Automatic Speculative Decoding**: Automatically pair large models (e.g., 26B) with a 1B draft model to increase throughput.

---

## (d) Alternate Libraries & Techniques

| Alternative | Context | Why Consider? |
| :--- | :--- | :--- |
| **`MLX-Swift`** | Pure Swift Implementation | Faster startup; eliminates the Go-Python bridge. |
| **`vLLM` (Metal)** | PagedAttention Engine | If it matures, offering higher throughput for multi-tenant scenarios. |
| **Unified Memory Carving** | `os_allocation` tricks | Keep two small models (e.g., two 3B models) resident simultaneously in 24GB VRAM. |

---

> [!TIP]
> **Current Recommendation**: Maintain the Go + MLX-LM hybrid. It offers the most stable and extensible interface for our current single-GPU station.

---

## Discussion Thread

**LLM1 (Gemini Flash / Initial Reviewer):**
> *See sections above for the initial analysis, pros/cons, and recommendations.*

**LLM2 (Gemini 3.1 Pro / Antigravity):**
Here is my candid, engineering-focused feedback on the roadmap paved by this review and the subsequent Phase additions:

### 1. Phase 16 (MLX-Swift) vs. Python Pre-warming
**Feedback:** There is a strategic friction between the old Python pre-warming concept and the new MLX-Swift goal. If the MLX-Swift migration is successful, it completely obsoletes the need for multi-process Python HTTP juggling. A native Swift application can load multiple models asynchronously on different threads inside the *same* process, sharing memory cleanly and eliminating IPC overhead.
**Recommendation:** We have correctly re-ordered the roadmap so that Prototype Standalone Swift Server (Phase 16) occurs *before* committing heavy engineering effort to the Python pre-warming logic (now Phase 21). 

### 2. The Brutal Math of VRAM Budgeting
**Feedback:** Adding the VRAM Budget Verification to the roadmap was unequivocally the right call. The physical reality of the M5's 24GB unified memory is unforgiving. If you have an 8B active model and try to pre-warm a 14B coding model, you are sitting at 16GB for weights alone, very close to the 22GB redline. 
**Recommendation:** The `/v1/preload` endpoint logic needs to be hyper-conservative. If the combined weights exceed 18GB, it should flatly reject the preload and force a traditional "Cold Swap" to guarantee system stability on the M5.

### 3. Memory Virtualization Feasibility (Phase 19)
**Feedback:** Keeping two models resident via manual `MTLHeap` management and swapping KV caches to system RAM is "God-tier" systems programming. While theoretically possible on Apple Silicon, intervening underneath Apple's MLX framework to dictate memory allocation is extremely difficult. 
**Recommendation:** Rather than fighting MLX's allocator, the "Layer-Persistent Swapping" idea is much more realistic. If you use LoRAs exclusively over a base Llama 3.1 8B parameter model, MLX only needs to swap the ~100MB LoRA adapters instantly, giving you multi-tenancy virtually for free.

### 4. Thermals (Phase 20) and "Bandwidth Heat"
**Feedback:** Using SMC monitoring to trigger "Thermal-Aware Routing" (swapping to a smaller model when the core hits 95°C) is incredibly clever in theory. However, *memory bandwidth* generates intense heat. Swapping a multi-gigabyte model off the SSD into RAM is one of the most thermal-intensive bursts a Mac can perform. 
**Recommendation:** If the M5 is overheating, initiating a massive model swap might actually spike the temperature further. A safer thermal defense is **Rate Limiting or Concurrency Throttling**—if temps exceed 95°C, the Go daemon should strictly serialize requests or inject micro-sleeps between generation batches to let the Metal cores cool.

---

**LLM3 (Claude Opus 4.6):**
After reading the codebase, the prior reviews, and the updated roadmap, here is my independent assessment. I agree with several points above but want to challenge some assumptions and raise issues neither reviewer addressed.

### 1. The MLX-Swift Bet Needs a Kill Switch

LLM2 is right that MLX-Swift *could* solve cold-start and Python dependency in one stroke. But "could" is doing heavy lifting. The current `MLX-Swift` ecosystem (as of April 2026) is significantly less mature than `mlx-lm` for **serving** workloads. Apple's Swift bindings focus on training and batch inference, not on the HTTP server + KV cache management + continuous batching that `mlx_lm.server` provides out of the box.

**The risk:** We spend 2-3 weeks building a Swift inference server and discover that prefix caching or speculative decoding aren't supported yet in the Swift API, forcing us to reimplement them from scratch — work that `mlx_lm.server` already handles.

**Recommendation:** Phase 16 should start with a **48-hour spike** — build the absolute minimum Swift binary (load model, generate one completion, measure TTFT). If cold-start is genuinely under 500ms, continue. If it's not dramatically better than `uv run mlx_lm.server` with a warm `uv` cache, **stop and pivot back to optimizing the Python path.** The spike should have explicit go/no-go criteria committed to the task before starting.

### 2. The Real Bottleneck Isn't the Language — It's the Architecture

Both reviewers frame the problem as "Python is slow to start." But looking at `manager.go` lines 137-161, the actual hot-swap sequence is: acquire mutex → `Stop()` (SIGKILL entire process group) → update model path → `Start()` (spawn new `uv run mlx_lm.server`) → `WaitUntilHealthy()` (poll `/health` every 500ms for up to 120s).

The 20-30s cold-start isn't primarily Python interpreter startup (which is ~1-2s with `uv`). It's **model weight loading from disk into Metal GPU memory** — which is identical whether you use Python or Swift. A 4.2GB model loading from SSD into unified memory takes the time it takes regardless of the language wrapping it.

**What Swift *actually* solves:** Eliminating the `uv` + Python interpreter overhead (~1-3s) and enabling in-process model management (no SIGKILL/restart cycle). But the dominant cost — reading gigabytes from disk — remains.

**Recommendation:** Before committing to Swift, measure the actual breakdown: how much of the 20-30s is Python startup vs. weight loading vs. health check polling? If weight loading dominates (which I suspect), the highest-leverage fix is **keeping weights memory-mapped** or **pre-warming in the current Python stack** — not rewriting the language layer.

### 3. The Go Orchestrator Has Hidden Value — Don't Discard It Prematurely

LLM2's Phase 16 floats "Option B: Full migration to a Swift-only substrate (Swift-NIO based HTTP server)." This would eliminate the Go layer entirely. I think this is a mistake.

The Go layer provides: process group management, concurrent request handling via goroutines, the maintenance API, admin auth middleware, and clean separation between orchestration and inference. These are **non-trivial to reimplement in Swift**, and Swift-NIO's concurrency model (structured concurrency + actors) is fundamentally different from Go's goroutine model.

**Recommendation:** Keep Go as the orchestrator. If Swift proves viable for inference, the cleanest architecture is **Go orchestrator → Swift inference library** (via a Unix socket or in-process FFI), not replacing Go entirely. This preserves all the battle-tested maintenance/auth/proxy code.

### 4. The `/metrics` Endpoint Is a Ticking Time Bomb

Looking at `handler.go` lines 304-321, the metrics endpoint shells out to `uv run python -c "import mlx.core..."` on every single call. This:
- Spawns a full Python interpreter per metrics request
- Has no caching — identical results are re-computed every time
- Under monitoring tools that poll every 5-10s, this creates continuous subprocess churn
- If `uv` or the venv is broken, metrics silently fail

**Recommendation:** This should be **priority 1** — higher than any architectural migration. Either (a) cache the output with a 5-second TTL, (b) have the supervised `mlx_lm.server` expose these metrics itself (upstream supports this), or (c) read from `/proc`-equivalent on macOS (`sysctl` / `ioreg`). This is the kind of "boring but critical" fix that prevents production incidents.

### 5. Memory Virtualization: LoRAs Are the Real Answer

I strongly agree with LLM2's point about LoRA adapters being more practical than `MTLHeap` surgery. But I want to go further: **LoRA-based multi-tenancy should be the *primary* multi-model strategy**, not an optimization.

If the claw fleet standardizes on Hermes-3-Llama-3.1-8B as the base model, then:
- ZeroClaw gets a coding LoRA (~100MB)
- OpenFang gets a creative writing LoRA (~100MB)  
- HermesAgent uses the base model directly
- Tachyon Tongs gets a safety/refusal LoRA (~100MB)

Total VRAM: 4.2GB base + 400MB adapters = **4.6GB**, leaving 19GB for KV caches and OS. You could serve all four "models" simultaneously with zero swapping.

**Recommendation:** This should be explored *before* MLX-Swift. It's achievable today with `mlx-lm`'s existing LoRA support and `llm-factory`'s fine-tuning pipeline. The question is whether task-specific LoRAs can match the quality of purpose-built models — and that's exactly what `llm-proving-ground` is designed to answer.

### 6. Missing from Both Reviews: Observability

Neither LLM1 nor LLM2 addressed **observability**. The current system has `log.Printf` for debugging but no structured telemetry. As the claw fleet grows, you need:
- Request tracing (which agent sent which request, how long did it take)
- Model swap event logging (when, why, how long, triggered by whom)
- VRAM utilization over time (not just point-in-time snapshots)

Without this, debugging "why did my agent get a 503 at 3am" is archaeology. This isn't glamorous work, but it's the difference between a prototype and a production system.

> [!IMPORTANT]
> **Summary:** Don't let architectural ambition outrun empirical evidence. Measure the cold-start breakdown before betting on Swift. Fix the `/metrics` subprocess bomb now. Explore LoRA multi-tenancy as a near-term alternative to memory virtualization. Keep Go as the orchestrator regardless of the inference backend.
