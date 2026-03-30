# Event Horizon Core: Tasks

## Phase 1: Environment & Setup [MUST COMPLETE]
- [ ] **OpenRouter Activation**:
    - [ ] Obtain API Key from [OpenRouter.ai](https://openrouter.ai/keys).
    - [ ] Copy `.env.template` to `.env`.
    - [ ] Add `export OPENROUTER_API_KEY="your_actual_key"` to your `~/.zshrc` (or fill `.env`).
    - [ ] Verify with `event-horizon status`.

## Phase 2: Performance & Connectivity [CURRENT]
- [x] VRAM Guard implementation (24GB limit enforcement).
- [x] OpenRouter remote fallback provider.
- [x] Comprehensive CLI `--help` with examples.
- [x] Agent Setup Guides (OpenClaw, ZeroClaw, OpenCode, etc.).
- [x] Repository security (`.gitignore` for secrets).

## Phase 3: Concurrency Torture Testing
- [x] Create `tests/test_torture.py` (Pytest-asyncio suite).
- [ ] Baseline Benchmark: Run torture tests and document failures/latencies.
- [ ] Monitor GPU/VRAM behavior during concurrent local calls.

## Phase 4: Orchestration Research & Selection
- [ ] **Investigate mlx_lm.server as native backend**:
    - [ ] Test OpenAI-compatible endpoints (`/v1/chat/completions`).
    - [ ] Verify `--prompt-cache-size` behavior with multiple agents.
    - [ ] Measure impact of `--decode-concurrency` on M5 GPU.
- [ ] **Review FEEDBACK_CONCURRENCY.md for alternatives**:
    - [ ] Research **vllm-mlx** (Continuous batching, Paged Attention).
    - [ ] Research **oMLX** (Two-tier KV Cache, SSD swapping).
    - [ ] Research **Sluice-LLM** (Priority-queue proxy).
    - [ ] Research **llama-swap** (Routing & model swapping).
    - [ ] Research **LiteLLM** (Proxying & unified queuing).
    - [ ] Evaluate **aiohttp / asyncio.Queue** (Custom priority worker loop).
- [ ] Implement selected orchestration strategy:
    - [ ] Cross-process locking for MLX (Metal).
    - [ ] KV Cache persistence/swapping (using `make_prompt_cache`).

## Phase 5: Extended Operations
- [ ] Add model "Shorthand" for OpenRouter (e.g. `best-free-coding`).
- [ ] Performance benchmark script (tok/s logger).
- [ ] Vision support (Gemma 3).
- [ ] Local RAG integration stub.
- [ ] Mobile/Edge deployment validation.
