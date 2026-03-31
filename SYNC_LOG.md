# Synchronization Log

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
