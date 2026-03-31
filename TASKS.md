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

## Phase 5: Native Architecture Integration [COMPLETE]
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
- [x] **Active Fallback Testing**:
    - [x] Get Llama.cpp up and running.
    - [x] Verify `uv run event-horizon llamacpp` successfully lists the model.
    - [x] Test Fallback: Saturated/timeout the MLX server verified.
- [x] **Next Capabilities [PHASE 5.4]**:
    - [x] Vision support (Gemma 3).
    - [x] Local RAG integration stub.
    - [x] Mobile/Edge deployment validation.

## Phase 6: Substrate Optimization (Resolved)
- [x] **Pivot from Ollama to Llama.cpp**:
    - [x] Legacy: Ollama retained as Tier 4 backup.
    - [x] Re-evaluated `llama.cpp` vs Ollama. `llama.cpp` provides direct C++/Metal execution without the Go abstraction. This pivot is fully migrated in Phase 5.3.

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
> <gemini_action_item: flash_model> **FLASH INSTRUCTIONS**: When Phases 7 and 8 are fully green and verified, systematically perform this cleanup safely.
- [x] Delete `event_horizon_core/orchestrator.py`.
- [x] Delete all provider implementations `event_horizon_core/providers/*.py`.
- [x] Strip `pyproject.toml` and `uv.lock` of any dependencies no longer needed by the core (e.g., `httpx`), retaining only what is needed for `mlx-lm` installation.
- [x] Remove `main.py` entrypoints if applicable and officially transition the repository root to the Go structure.
- [x] Close out `TASKS.md` Phase 9 as Complete.
