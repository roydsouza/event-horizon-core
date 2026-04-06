# MLX Multiplexing & Multi-Model Serving: Options Review

> **Status**: Research / Pre-decision
> **Author**: Claude Code, 2026-04-04
> **Context**: EHC currently wraps `mlx_lm.server` with sequential hot-swap. This doc
> captures known alternatives for better concurrent and multi-model serving on Apple Silicon
> before any backend change is committed to.
>
> **Decision needed from operator**: Which direction, if any, to pursue after broader research.

---

## Current Baseline: EHC + mlx_lm.server

**Architecture**: Go daemon proxies to a single `mlx_lm.server` (Python) subprocess.
Model switching is SIGKILL → restart. The concurrent-client mutex fix (commit 9ad2cbf)
serializes hot-swaps and protects field reads — but does not change the fundamental
single-model, sequential-swap nature of the stack.

**Known issues in mlx_lm.server** (upstream GitHub issues):

| Issue | Severity | Description |
|:------|:---------|:------------|
| KV cache cross-contamination (#965) | Critical | At 16+ concurrent requests, responses bleed across clients |
| Batch KV merge crash (#754) | High | Mixed cached/empty batch causes crash at higher concurrency |
| Cache poisoning across requests (#975) | High | Sequential requests retain "memory" from prior prompt |
| Kernel panic on long contexts (#883) | High | ~58K+ token context causes OS-level crash |
| Prefix cache broken for hybrid models (#980) | Medium | Sliding window / Mamba architectures unsupported |

**Upshot**: mlx_lm.server has correctness bugs under concurrent load that EHC's mutex
fix cannot paper over — the bugs are in the Python subprocess itself, not in Go.

---

## Option 1: vllm-mlx

**Repo**: github.com/waybarrios/vllm-mlx
**Paper**: arxiv.org/html/2601.19139v2 (published, benchmarked on M4 Max)
**Maturity**: Beta — active development, community-driven, not Apple-official

### What it fixes vs. baseline

- **Concurrent clients, same model**: Explicit token-level dynamic scheduler with tested
  4.3x throughput scaling at 16 concurrent requests. No KV cache contamination issues.
- **KV cache**: Paged KV + SHA-256 prefix caching → 5.8x TTFT speedup for shared prefixes;
  19x for cached multimodal queries. Drop-in replacement for mlx_lm.server HTTP API.
- **Robustness**: No kernel panic / unbounded growth issues reported.

### What it does NOT fix

- **Multi-model**: Single model at a time — no native hot-swap or multi-model pool.
  External orchestration required (see Option 3).
- **Context length**: Gemma 3 sliding window caps at ~10K tokens due to Metal GPU timeout.
- **paged attention**: Still marked experimental.

### Adoption cost

EHC's Go handler already proxies to a fixed port (`127.0.0.1:8080`). Swapping the backend
from `mlx_lm.server` to `vllm-mlx` is one line in `manager.go`. API is OpenAI-compatible.
The `--prompt-cache-size` flag would need to be replaced with vllm-mlx's equivalent flag.

### Open questions before committing

- [ ] Does vllm-mlx handle the same models we use (Hermes-3, Qwen, Llama-3)?
- [ ] What is the actual TTFT and throughput on M5 vs M4 Max in the paper?
- [ ] Is the Metal GPU timeout for long contexts configurable?
- [ ] Does it expose the same `/v1/chat/completions` endpoint with identical semantics?
- [ ] Last commit date and maintenance velocity — is it still active?
- [ ] Does it support speculative decoding (we use `MLX_DRAFT_MODEL`)?

---

## Option 2: mlx-lm-server (Apple's own server improvements)

**Note**: The upstream `mlx-lm` project (`github.com/ml-explore/mlx-lm`) actively develops
its own server. Many of the bugs listed above have open PRs or are addressed in recent
versions. Before replacing the backend, it is worth checking:

- [ ] Current version of `mlx_lm` — are the concurrency bugs (#965, #754, #975) fixed?
- [ ] Does the current `mlx_lm.server` support `--max-requests` or backpressure?
- [ ] Is there a `--kv-cache-strict-isolation` or similar flag?

**Adoption cost**: Zero if the bugs are already fixed upstream — just `uv update mlx_lm`.

This should be verified **before** evaluating any alternative backend, since it may
render the problem solved with no architecture change.

---

## Option 3: Multi-instance Pool (vllm-mlx or mlx_lm.server)

For true multi-model serving on 24GB: run N instances of the backend (one per model),
each on a distinct port, and route in EHC's Go handler by model name.

```
EHC handler.go
  ├── model "hermes-3-8b"   → 127.0.0.1:8081 (vllm-mlx instance A, 5GB VRAM)
  ├── model "qwen-7b"       → 127.0.0.1:8082 (vllm-mlx instance B, 5GB VRAM)
  └── model "default"       → 127.0.0.1:8080 (primary instance, remainder of VRAM)
```

**VRAM budget on 24GB**: Two 8B-4bit models (~5GB each) + one 7B (~4.5GB) leaves ~9GB for
KV cache and OS — viable for 2–3 small models simultaneously.

**Adoption cost**: Medium — requires a model registry in EHC config, port-per-model
allocation, and a routing layer in handler.go. No SIGKILL-based swap at all.

**Open questions**:
- [ ] What is the actual per-model VRAM footprint for our models at 4bit?
- [ ] Does MLX release VRAM immediately on process exit, or is there a delay?
- [ ] Is there an mlx utility that reports per-process GPU memory allocation?

---

## Option 4: vLLM Sleep Mode (not yet on Apple Silicon)

vLLM (CUDA, not MLX) implements "Sleep Mode": a loaded model can be suspended to CPU RAM
(level 1: 0.1–6s wake) or disk (level 2: slower). This is **not ported to MLX / Apple Silicon**
as of 2026-04-04. It would require porting vLLM's memory management to the unified memory
architecture where the CPU/GPU boundary doesn't exist in the same way.

**Track but do not implement now.** If the vllm-mlx project adds sleep mode, this becomes
the best answer for multi-model with minimal VRAM overhead.

---

## Option 5: ActivatedLoRA / aLoRA (multi-adapter, not multi-model)

**Paper**: "Efficient Multi-Adapter LLM Serving via Cross-Model KV-Cache Reuse" (2025)
**What it is**: Share a single base model in memory; hot-swap only the LoRA adapter weights
(much smaller). Cross-model prefix caching reuses base model KV states across adapters.
**Reported speedup**: 20–30x per-task completion; 5x end-to-end.

**Applicability**: Only relevant if our "multiple models" are fine-tuned variants of the
same base (e.g., a general Hermes-3 + a code-specialized Hermes-3-Code LoRA). If the
"models" are architecturally distinct (Hermes-3 vs. Qwen), this does not apply.

**Status on MLX**: Not ported. vLLM CUDA only.

---

## Option 6: MLX-LM Model Sharding / Pipeline Parallelism

MLX supports tensor parallelism across CPU and GPU on Apple Silicon (unified memory makes
this interesting — no PCIe transfer). For very large models (32B+) that don't fit in VRAM,
pipeline parallelism across layers is possible but adds significant latency per token.

This is **not relevant to the multi-client/multi-model problem** — it addresses single
very-large-model serving, not concurrency.

---

## Recommendation Order (preliminary — needs more research)

1. **First**: Check if upstream `mlx_lm` has fixed the concurrency bugs in recent versions.
   Cost: zero. May close the issue entirely.

2. **If not fixed**: Evaluate vllm-mlx with a local benchmark on M5 — run the same
   concurrent request test used in `tests/stress_test.go` and compare throughput and
   error rates against mlx_lm.server at the same version.

3. **For multi-model**: Prototype the multi-instance pool (Option 3) with two vllm-mlx
   instances and a simple routing table in handler.go. This is independent of the
   single-model concurrency question.

4. **Watch**: vLLM Sleep Mode on Apple Silicon. If it lands in vllm-mlx, it supersedes
   the multi-instance pool approach with better VRAM efficiency.

---

## Research Still Needed

Before any decision:

- [ ] **mlx_lm upstream changelog**: Are the concurrency bugs fixed in current `pip install mlx_lm`?
- [ ] **vllm-mlx model compatibility**: Does it load `mlx-community/Hermes-3-Llama-3.1-8B-4bit`?
- [ ] **vllm-mlx speculative decoding**: Does it support draft model acceleration?
- [ ] **Any other MLX-native serving projects**: ollama (uses llama.cpp not MLX),
  LMStudio (closed source), anything else building on `mlx` directly?
- [ ] **mlx.distributed**: Apple's own multi-device tensor parallelism — any server mode?
- [ ] **llamafile + MLX**: Does llamafile have an MLX backend or Apple Silicon optimizations?

