# MLX Multiplexing & Multi-Model Serving: Options Review

> **Status**: Research complete — awaiting operator decision on Phase 15 direction
> **Authors**: Claude Code (2026-04-04 initial), updated 2026-04-07 with web research
> **Context**: EHC wraps `mlx_lm.server` with sequential hot-swap. This doc captures
> alternatives for better concurrent and multi-model serving on the M5 24GB before any
> backend change is committed to.
>
> **Jump to decision**: [Recommendation](#recommendation-decision-tree)

---

## Current Baseline: EHC + mlx_lm.server (pinned 0.31.1)

**Architecture**: Go daemon proxies to a single `mlx_lm.server` (Python) subprocess.
Model switching is SIGKILL → restart. EHC's mutex fix (commit 9ad2cbf) serializes
hot-swaps and protects field reads — but does not change the fundamental single-model,
sequential-swap nature of the stack.

**Known issues — updated status as of 2026-04-07:**

| Issue | Severity | Description | Status in 0.31.2 |
|:------|:---------|:------------|:-----------------|
| KV cache cross-contamination (#965) | Critical | At 16+ concurrent requests, responses bleed across clients | ✅ **FIXED** — PR #976, merged 2026-03-10 |
| Batch KV merge crash (#754) | High | Mixed cached/empty batch causes crash at higher concurrency | ✅ **FIXED** — PR #755, merged 2026-01-14 |
| Cache poisoning across requests (#975) | High | Sequential requests retain "memory" from prior prompt | ⚠️ **Contested** — nominally closed 2026-03-27; original reporter disputed the fix; treat cautiously |
| Kernel panic on long contexts (#883) | High | `IOGPUMemory` crash at ~58K+ token context | ⚠️ **Mitigated** — `--max-kv-size` flag added (PR #906); underlying Metal/IOGPUMemory driver bug unresolved; user reports continued panics on M3 Ultra as of 2026-03-31 |
| Prefix cache broken for hybrid models (#980) | Medium | Sliding window / Mamba architectures unsupported | Not tracked |

**Current latest upstream**: `mlx-lm 0.31.2`, released **2026-04-07** (today). We are
pinned to `0.31.1`. The two critical bugs (#965, #754) are fixed in 0.31.2.

**New flags in recent upstream versions (not yet in our config):**
- `--decode-concurrency N` (default 32): max concurrent decode requests
- `--prompt-concurrency N` (default 8): max concurrent prefill requests
- `--max-kv-size N`: hard cap on KV cache memory to prevent #883

---

## Option A: Upgrade mlx-lm to 0.31.2 (zero architecture change)

**Cost**: One line — change `mlx-lm==0.31.1` → `mlx-lm==0.31.2` in `pyproject.toml`.
Add `--max-kv-size 8192` to the `args` slice in `manager.go` `Start()`.

**What this fixes:**
- #965 (KV cross-contamination) — confirmed fixed
- #754 (batch merge crash) — confirmed fixed
- #883 (kernel panic) — mitigated via `--max-kv-size` cap

**What remains:**
- #975 (cache poisoning) — fix contested; may or may not affect our usage pattern
- The IOGPUMemory driver bug (#883) exists at the OS level; the flag prevents hitting it

**Verdict**: Almost certainly sufficient for our actual concurrency level (2–5 agents,
not 16+). The concurrency bugs were triggered by stress conditions we don't hit in
normal operation. This should be done **first**, before evaluating any alternative backend.

**Risks:**
- 0.31.2 introduced batch generator refactoring — regression possible; run stress tests
- #975 fix contested — do a regression test with multi-turn agents after upgrade

---

## Option B: vllm-mlx (community alternative backend)

**Repo**: github.com/waybarrios/vllm-mlx · **PyPI**: `pip install vllm-mlx`
**Stars**: 774 · **Last active**: Feb 2026 · **Paper**: accepted EuroMLSys '26

### What it fixes vs. our baseline

- **Concurrent clients, same model**: Explicit token-level scheduler; tested 4.3x
  throughput at 16 concurrent requests; no KV contamination issues.
- **KV cache**: Paged KV + SHA-256 prefix caching (1.55x speedup at 66.7% hit rate).
  19x TTFT improvement for cached multimodal queries.
- **API**: Fully OpenAI-compatible `/v1/chat/completions`. Also exposes Anthropic
  Messages API `/v1/messages`.
- **Continuous batching**: Available via `--continuous-batching` (must be explicitly
  enabled). `--max-num-seqs 256` for concurrency cap.

### What it does NOT fix

- **Speculative decoding**: **Not supported.** vllm-mlx PR #180 added speculative
  *prefill* (different concept — sparse draft for TTFT), but standard draft-model
  speculative *decode* (our `MLX_DRAFT_MODEL` feature) is absent. **Adopting vllm-mlx
  means losing speculative decoding.**
- **Multi-model**: Single model at a time. External orchestration still required.
- **M5 benchmarks**: All published data is on M4 Max 128GB. No M5 numbers.
- **Metal timeout**: Single `--timeout` flag (default 300s); no Metal-specific knob.

### Adoption cost (EHC side)

Swap the `uv run mlx_lm.server` launch command in `manager.go` `Start()` for
`vllm-mlx serve`. Replace `--prompt-cache-size` with vllm-mlx equivalents. The Go
proxy layer (port 8080 target) is unchanged.

### Verdict

Only worth the speculative-decoding trade-off if Option A fails to resolve the
concurrency issues at our actual load. Evaluate only after confirming 0.31.2 is
insufficient.

---

## Option C: Multi-Instance Pool (EHC routing by model name)

Eliminate hot-swap entirely. Run N backend instances (one per model, each on a
distinct port), route by model name in EHC's Go handler.

```
handler.go routing table
  "hermes-3-8b"   → 127.0.0.1:8081  (4.2 GB Metal)
  "llama-3.2-3b"  → 127.0.0.1:8082  (1.7 GB Metal)
  "default"       → 127.0.0.1:8081  (same as hermes)
```

**VRAM budget on 24GB M5:**

| Model | Metal footprint |
|:------|:----------------|
| Hermes-3-Llama-3.1-8B-4bit | ~4.2 GB |
| Llama-3.2-3B-Instruct-4bit | ~1.7 GB |
| gemma-4-e4b-it-4bit | ~4.9 GB |
| OS + KV cache headroom | ~6–8 GB |

Two-model pool (Hermes + Llama) uses ~6 GB Metal, leaves ~18 GB for OS + KV cache.
Three-model pool (Hermes + Llama + Gemma-4-e4b) uses ~11 GB Metal — still viable with
our 22 GB cap.

**Adoption cost**: Medium — add model registry to `config.toml`, change `ProcessManager`
to manage a map of port-per-model instances, update routing logic in `HandleCompletions`.
This is the Phase 24 routing table work (already designed) plus `ProcessManager` pool
semantics.

**Verdict**: The right long-term architecture once we have 3+ active agents needing
distinct models simultaneously. Depends on Phase 24 routing table (already designed in
TASKS.md). Not urgent while we have only one or two active agents.

---

## Option D: oMLX (jundot/omlx) — macOS-native serving app

**Repo**: github.com/jundot/omlx · **Release**: v0.3.5.dev1, 2026-04-07
**Type**: Native macOS menu bar app + web dashboard, signed and notarized

### What it offers

- **SSD KV cache**: Hot blocks in RAM, cold blocks on SSD in safetensors format with
  LRU eviction. Reduces TTFT on long agent contexts from 30–90s → <5s.
- **Multi-model LRU eviction**: Loads multiple models, evicts least-recently-used when
  VRAM is needed. Continuous batching with up to 4.14x speedup at 8x concurrency.
- **OpenAI + Anthropic APIs**: `/v1/chat/completions` and `/v1/messages`.
- `max_concurrent_requests` concurrency cap.

### Concerns for our setup

- **RAM requirement**: Documentation states 64 GB+ RAM recommended. We have 24 GB.
  SSD KV cache tiering is designed to offset VRAM pressure on larger memory systems;
  its behavior on a 24 GB M5 with a 4.6 GB pinned model is untested.
- **Closed-source app**: Cannot inspect the serving logic, pin a version in `pyproject.toml`,
  or automate startup from EHC's supervisor. Integration with EHC's `ProcessManager`
  (which uses `exec.Command` + process group control) would be nonstandard.
- **Overlapping responsibility**: oMLX is itself an LLM server manager. Wrapping it
  inside EHC creates two competing supervisors.

### Verdict

Interesting for a workstation with 64 GB+ where the SSD cache tiers work as designed.
On our 24 GB M5, the RAM constraint and closed-source supervisor conflict make it a
poor fit. **Do not pursue for EHC integration.** Worth watching for future hardware
upgrades.

---

## Option E: vllm-metal (official vLLM Apple Silicon plugin)

**Repo**: github.com/vllm-project/vllm-metal
Routes through MLX as the compute backend; official vLLM project umbrella.

- Paged attention: experimental (`VLLM_METAL_USE_PAGED_ATTENTION=1`); ~82x TTFT and
  3.75x throughput improvement on Qwen3-0.6B in early benchmarks.
- **No sleep mode** — vLLM sleep mode (level 1/2) is CUDA/ROCm only, not ported to Metal.
- Less mature than vllm-mlx for Apple Silicon; benchmarks only on small models.

**Verdict**: Track but do not pursue. Less battle-tested than vllm-mlx for our stack.
If vllm-metal adds sleep mode, that changes the calculus entirely — it would supersede
the multi-instance pool approach for multi-model serving.

---

## Options Not Pursued

| Option | Why Not |
|:-------|:--------|
| **Ollama 0.19** (MLX backend) | Switched from llama.cpp to MLX in v0.19 preview (2026-03-30). But Ollama's wrapper adds process management overhead and its API fidelity vs. raw mlx_lm.server is uncertain. Not worth adding a dependency. |
| **mlx.distributed** | Multi-machine tensor parallelism transport layer. Not a serving framework. Not relevant to single-machine multi-client problem. |
| **llamafile** | GGML/Metal only, no MLX backend. Inferior throughput on M5. |
| **ActivatedLoRA / MOLA** | Only relevant if all "models" are adapters of the same base. Our agent fleet uses architecturally distinct models. MOLA interesting for the `llm-factory` / fine-tuned adapter case. |
| **vLLM sleep mode** | CUDA only as of today. Watch vllm-metal repo for Apple Silicon port. |
| **MLX-Swift (Phase 16)** | E1 data: NO-GO. Python startup is ~202ms constant; weight loading dominates. |

---

## Recommendation: Decision Tree

```
START
  │
  ▼
Step 1: Upgrade mlx-lm 0.31.1 → 0.31.2
        Add --max-kv-size 8192 to manager.go
        Run stress tests at 5 concurrent clients
        │
        ├─ Tests pass, no #975/#883 regressions?
        │   → DONE. No further backend change needed.
        │     (Phase 15 complete. Resume Phase 25.)
        │
        └─ Still seeing contamination or crashes?
            │
            ▼
        Step 2: Evaluate vllm-mlx
                - Install: uv add vllm-mlx
                - Run same stress tests
                - Benchmark TTFT with and without spec decoding
                  to quantify the speculative-decode regression
                │
                ├─ Acceptable? (concurrency fixed, TTFT acceptable)
                │   → Switch backend in manager.go
                │
                └─ TTFT regression too large?
                    → Stay on mlx-lm 0.31.2, live with #975 risk,
                      document the exposure in LIMITATIONS.md

SEPARATELY (independent of above):
  Multi-model pool (Option C) — implement as part of Phase 24
  routing table work when 3+ agents need simultaneous distinct models.
  Not a concurrency fix; a different architectural goal.
```

### Implementation plan for Step 1 (if Roy approves)

**`pyproject.toml`** — one line:
```
mlx-lm>=0.31.2,<0.32
```

**`manager.go` `Start()` — add one arg** to the `args` slice:
```go
"--decode-concurrency", "16", // sensible cap for our 2-5 agent fleet; default is 32
```

> **Note on `--max-kv-size`**: this flag does not exist on `mlx_lm.server`. PR #906 added
> KV size limits internally in the server logic, not as a CLI flag. For #883 mitigation,
> the practical protection is avoiding 58K+ token contexts (not a concern for our agent fleet).

**Regression test protocol:**
```bash
# After uv sync:
uv run python -c "from mlx_lm.models import gemma4; print('ready')" # Phase 13 check
uv run python tests/hardware_benchmark.py                             # TTFT baseline
# Run stress test (if it exists) at 5 concurrent clients
# Confirm multi-turn agent context is not poisoned (#975)
```

---

## Research Gaps Resolved

All open questions from the original doc are now answered:

| Question | Answer |
|:---------|:-------|
| Are the concurrency bugs fixed upstream? | #965 + #754: yes in 0.31.2. #975: contested. #883: mitigated. |
| vllm-mlx — Hermes-3-8B support? | Likely yes (all mlx-community quantized models stated compatible) |
| vllm-mlx — speculative decoding? | **No.** Draft-model decode not supported. |
| vllm-mlx — M5 benchmarks? | None published. M4 Max 128GB only. |
| vllm-mlx — same /v1/chat/completions semantics? | Yes, fully OpenAI-compatible. |
| mlx.distributed — server mode? | No. Transport layer only. |
| llamafile — MLX backend? | No. GGML/Metal. |
| Other MLX-native serving? | oMLX (64GB+ focus), vllm-metal (early), MOLA (LoRA-only). |
| vLLM sleep mode on Apple Silicon? | Not ported. CUDA only. Watch vllm-metal. |
