# Synchronization Log

- **2026-03-31 14:00:00 PDT**: **Phase 9: Python Eradication & Final M5 Optimization Complete**.
    - **Thin-Client Refactor**: Overhauled `event_horizon_core/cli.py` to act as a high-speed proxy. It now utilizes the `requests` library to communicate with the Go Daemon on Port 8000, preserving the `uv run event-horizon` workflow while offloading all logic to the Go substrate.
    - **Logic Purge**: Deleted `orchestrator.py`, `factory.py`, and the entire `providers/` directory. All manual VRAM locking, queueing, and fallback logic is now handled natively by Goroutines and blocking Go middleware.
    - **Dependency Pruning**: Cleaned up `pyproject.toml`, removing `httpx`, `pydantic`, and `pytest-asyncio`. Added `requests` as the sole networking dependency for the CLI. Retained `mlx-lm` for the supervised inference engine.
    - **Verification**: Confirmed `uv run event-horizon status` and `generate` commands are fully functional and correctly trigger hot-swaps in the background daemon. 
    - **Hardware State**: Prefix Caching and Speculative Decoding are active by default in the Go supervisor, achieving optimal TTFT on the Apple Silicon M5.

- **2026-03-31 12:00:00 PDT**: **Architectural Handoff: Go Daemon Migration & Dynamic Model Swapping**.
    - **Decision**: Python is being retired for the orchestration layer. The Go Standard Library (`net/http`) will replace it to support an ultra-low footprint, massively concurrent REST proxy on port `8000`.
    - **Active Supervision**: Go `os/exec` will manage `mlx_lm.server` (Tier 1) and `llama-server` (Tier 2).
    - **Anti-Zombie Strategy**: Subprocesses will be tied to Process Groups (`syscall.SysProcAttr{Setpgid: true}`) so that a single `SIGKILL` destroys the entire execution tree if the Go proxy crashes.
    - **Dynamic Model Swapping**: Approved. If a client requests a model not currently active in VRAM, the Go daemon will intercept the HTTP request, cleanly terminate the active MLX server, boot the new model, wait for port health, and then release/forward the request. Clients will experience a TTFT delay (e.g., ~3-5 seconds) rather than a failure.
    - **handoff_instructions_for_junior_model (Flash)**: 
        1. Initialize `go mod` and set up the `net/http` router.
        2. DO NOT use Fiber or external web frameworks. Stick to `net/http`.
        3. Implement the `os/exec` supervision exactly as described above to avoid memory leaks.
        4. Refer to `TASKS.md` Phases 7-9 for the step-by-step implementation plan.

- **2026-03-31 06:25:00 PDT**: **Phase 5: Substrate Refactor and Provider Pivots**.
    - **Performance Benchmarking**: Created `scripts/bench_performance.py` mapping TTFT and tok/s. Confirmed MLX native achieves ~52 tok/s vs Ollama's ~15 tok/s for comparable Llama 3 parameters on the M5 chip.
    - **Telemetry Upgrade**: Overhauled BaseLLMProvider to return a structured `ProviderResponse` object containing `UsageMetadata` (token tracking and generation time metrics). Integrated real-time performance footer into CLI responses.
    - **Phase 5.3: Fallback Engine Pivot (Ollama -> Llama.cpp)**: 
        - Re-evaluated Ollama vs `llama.cpp` for secondary GGUF provisioning. 
        - Identified Ollama's Go-based wrapper abstraction as introducing unnecessary memory management overhead relative to pure C++/Metal bindings.
        - Pivoted architecture to utilize a native `llama-server` (installed via Homebrew for optimal ANE/AMX compilation on M5) listening on port 8081.
        - Removed `ollama_provider` as default fallback, relegating it to legacy (Tier 4). Created `LlamaCppProvider` as Tier 2 fallback.
    - **CLI Enhancements**: Restored `--help` command with extensive hierarchy documentation. Added provider-specific model listing commands (`event-horizon [mlx|llamacpp|ollama|openrouter]`).

- **2026-03-31 00:35:12 PDT**: **Phase 4: Advanced Native Substrate Finalized**. 
    - **Inference Benchmark (mlx-lm 0.31.1)**:
        - **Cold Start**: 4.06s TTFT for Llama-3.2-3B.
        - **Warm Cache**: 1.61s TTFT (60% reduction) via native `--prompt-cache-size`.
        - **Concurrency**: Verified 100% success rate with 2 simultaneous processes (6 agents total) hitting a single Metal instance.
    - **Architectural Decision**: Officially moved to a **Remote Native Provider** (wrapping `mlx_lm.server`). This replaces the custom `LocalInferenceQueue` and `asyncio` semaphore logic with the more robust upstream implementation.
    - **Paths Not Taken (Historical Record)**:
        - **vllm-mlx**: Bypassed due to its status as a 3rd-party port. Official `mlx_lm.server` now includes Continuous Batching and Paged Attention equivalent features in our target version (0.31.1).
        - **oMLX**: Bypassed for the current 2GB-8GB model range. SSD-swapping is a viable Phase 7 upgrade if we move to 70B+ models on the 24GB M5, but RAM-based caching is superior for current latency targets.
        - **Sluice-LLM / llama-swap**: Bypassed to avoid "Proxy Layer Bloat." Since the native server handles its own JSON-RPC serialization, additional middleware would increase TTFT without adding security or performance value.
        - **Custom KV Swap**: Bypassed implementation of `make_prompt_cache` and `mx.save_safetensors` as it effectively duplicates the server's internal context management logic.
- **2026-03-30 23:55:24 PDT**: **Phase 3: Stress Testing & Torture Results**. 
    - Identified Ollama Go-wrapper as a 60s timeout bottleneck at 3+ concurrent agents.
    - Confirmed MLX process-level stability up to 2 concurrent agents, but found "The Race" (simultaneous launch) would thrash the Metal queue.
    - Verified M5 24GB unified memory guard at 22GB effectively protects OS UI stability.
- **2026-03-29 22:06:37 PDT**: Finalized Phase 2: Documentation complete, CLI help expanded, and Concurrency Torture Tests added.
