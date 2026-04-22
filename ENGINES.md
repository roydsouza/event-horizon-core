# 🌌 Local LLM Inference Engines: 2026 Apple Silicon Review

This document provides a comparative analysis of the leading local LLM inference engines for Apple Silicon (M-series) as of April 2026. It highlights the strengths, weaknesses, and ideal use cases for each, specifically focused on the constraints of the M5 24GB Unified Memory architecture.

---

## 🚀 Engine Comparison Matrix

| Engine | Primary Backend | Best For... | Speculative Decoding | Continuous Batching | Multi-Model Strategy |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **MLX-LM** | MLX (Native) | Throughput / Research | ✅ Yes | ⚠️ Limited | Sequential Swap |
| **vLLM-MLX** | MLX / Paged KV | Concurrent Agents | ❌ No | ✅ Yes | Single Model |
| **Ollama** | MLX / llama.cpp | Developer Ergonomics | ❌ No | ⚠️ Basic | Automatic Swapping |
| **llama.cpp** | Metal (GGUF) | Compatibility | ✅ Yes | ✅ Yes | Multi-Slot (RPC) |
| **Bodega** | Metal / MLX | Production Agents | ✅ Yes | ✅ Yes | Native Multiplexing |
| **oMLX** | MLX | Massive Contexts | ❌ No | ✅ Yes | SSD-backed LRU |

---

## 🗝️ Key Terms

### Speculative Decoding
A performance optimization where a smaller, faster "draft" model predicts the next few tokens, which are then verified in parallel by the larger "target" model. If the target model agrees, multiple tokens are generated in a single step, significantly increasing tokens-per-second (TPS) without losing quality.

### Continuous Batching
A scheduling technique that allows the engine to process multiple requests simultaneously by inserting new requests into the generation loop as soon as an existing request finishes a token. Unlike static batching, it prevents "head-of-line blocking" where one long request stalls others.

### Multi-Model Strategy
The architectural approach to managing multiple LLMs on a single machine. 
- **Sequential Swap**: Unloads the current model to load a new one (high latency).
- **Model Pool**: Keeps multiple models resident in VRAM (high memory usage).
- **LRU/SSD Eviction**: Dynamically moves model weights between VRAM, RAM, and SSD based on recent usage.

### Primary Backend Types
- **MLX (Native)**: Uses Apple's `mlx` array framework directly. Optimized for Apple Silicon's Unified Memory and provides the most direct path to the GPU/Neural Engine.
- **Metal (GGUF)**: Uses the `llama.cpp` Metal backend to run GGUF-formatted models. Highly portable and memory-efficient, but doesn't use the MLX framework's specific optimizations.
- **MLX / Paged KV**: Combines the MLX compute kernels with "Paged Attention" memory management (similar to vLLM). This allows for much more efficient KV cache utilization, enabling higher concurrency.
- **Metal / MLX**: A hybrid approach (often found in Bodega) that uses MLX for heavy compute while utilizing custom Metal kernels for specialized tasks like prefix caching or speculative decoding verification.
- **MLX (SSD-Backed)**: An MLX implementation that has been modified to support swapping context blocks to/from the SSD, allowing for massive context windows that exceed physical RAM.

---

## 🛠️ Detailed Deep Dives

### 1. MLX-LM (`mlx_lm.server`)
The reference implementation from Apple's machine learning team.
- **Highs**: Absolute maximum raw throughput on Metal; zero-day support for new Apple Silicon features (ANE/AMX); native support for 4-bit quantization.
- **Lows**: High cold-start latency (1.9–3.8s on M5); Python-heavy overhead; basic request queueing (lacks sophisticated scheduling).
- **Ideal Use**: Single-agent high-speed reasoning; model evaluation.

### 2. vLLM-MLX / vLLM-Metal
The community port of the high-throughput vLLM engine to Apple Silicon.
- **Highs**: Paged Attention (82x TTFT improvement on small models); Continuous Batching allows 4x throughput at 16+ concurrent requests.
- **Lows**: Experimental status; lacks speculative decoding (draft models); higher memory floor for the Paged KV cache.
- **Ideal Use**: Serving a single powerful model to a large fleet of lightweight agents.

### 3. Ollama
The "Gold Standard" for developer experience.
- **Highs**: Massive model library; easiest setup; recently adopted MLX as a primary backend for Mac, significantly closing the performance gap with native tools.
- **Lows**: Abstraction overhead; difficult to tune internal hyperparameters (like KV cache size) compared to raw engines.
- **Ideal Use**: General development; non-performance-critical agent orchestration.

### 4. llama.cpp
The "Swiss Army Knife" of local LLM.
- **Highs**: Universal compatibility (GGUF); supports almost every quantized format; very low memory overhead; extremely stable.
- **Lows**: Raw throughput is often 10-20% lower than MLX-native on M-series chips; complex CLI flags.
- **Ideal Use**: Systems requiring maximum stability or support for non-standard model architectures.

### 5. Bodega / Bodega One
Production-focused Apple Silicon inference.
- **Highs**: Native prefix caching (huge win for long-context agents); built-in support for speculative decoding; high-integrity serving.
- **Lows**: Often bundled as part of the Bodega One IDE app; standalone server version has a smaller community than Ollama.
- **Ideal Use**: Dedicated "Dark Factory" stations; high-reliability agentic workflows.

### 6. oMLX
Specialized for memory-constrained systems (like the 24GB M5) needing massive context.
- **Highs**: **SSD-backed KV caching**. Evicts cold context blocks to the SSD, allowing for contexts larger than physical RAM.
- **Lows**: SSD latency is significantly higher than RAM; requires high-speed NVMe for acceptable performance; 64GB+ RAM still recommended for best results.
- **Ideal Use**: Long-chain reasoning agents where context persistence is more important than raw tokens-per-second.

---

## 📊 Strategic Recommendation for Antigravity

For the **M5 24GB** hardware boundary:

1. **Production Backbone**: Stay with **MLX-LM** (via Go Substrate) for the 8B-11B "Tier 1" models. The speculative decoding support is a force multiplier for agent responsiveness.
2. **The "vLLM-MLX" Pivot**: Consider only if the agent fleet grows to 10+ concurrent consumers where continuous batching becomes necessary.
3. **The "oMLX" Watch**: Monitor SSD-backed KV caching. If we move to 70B+ models on this hardware, oMLX becomes the only viable path.
