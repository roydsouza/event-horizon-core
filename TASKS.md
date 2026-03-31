# Event Horizon Core: Tasks

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

## Phase 5: Native Architecture Integration [IN PROGRESS]
- [x] **Refactor MLX Backend**: 
    - [x] Implementation: Refactor `MLXProvider` into `RemoteNativeProvider` wrapping `mlx_lm.server`.
    - [x] Verification: Test concurrent multi-agent requests via CLI. (Confirmed 1.53s avg latency).
- [x] **Extended Capabilities [PHASE 5.2]**:
    - [x] **OpenRouter Model Shorthand**: Implement aliasing.
    - [x] Performance benchmark script (tok/s logger).
- [x] **Native Llama.cpp Integration [PHASE 5.3]**:
    - [x] Install Homebrew `llama.cpp` for native M5 Metal optimization.
    - [x] Implement `LlamaCppProvider` (Tier 2 fallback).
    - [x] Update Orchestrator and CLI to route to `llamacpp` on port 8081.
- [ ] **Active Fallback Testing**:
    - [ ] Get Llama.cpp up and running: Download a test `.gguf` and run `llama-server -m <model.gguf> --port 8081`.
    - [ ] Verify `uv run event-horizon llamacpp` successfully lists the model.
    - [ ] Test Fallback: Saturated/timeout the MLX server and verify Orchestrator successfully hands off the generation to the Llama.cpp server.
- [/] **Next Capabilities [PHASE 5.4]**:
    - [ ] Vision support (Gemma 3).
    - [ ] Local RAG integration stub.
    - [ ] Mobile/Edge deployment validation.

## Phase 6: Substrate Optimization (Resolved)
- [x] **Pivot from Ollama to Llama.cpp**:
    - [x] Legacy: Ollama retained as Tier 4 backup.
    - [x] Re-evaluated `llama.cpp` vs Ollama. `llama.cpp` provides direct C++/Metal execution without the Go abstraction. This pivot is fully migrated in Phase 5.3.
