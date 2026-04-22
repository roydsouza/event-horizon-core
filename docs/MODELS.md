# 📖 Supported Models (M5 24GB Optimized)

> [!CAUTION] 
> **Hardware Boundary Limitations (M5 24GB)**
> As of **April 2026**, our concurrency benchmarking (`TEST_RESULTS.md`) confirms that 24GB of Unified Memory is the critical threshold for multi-agent workloads. To maintain a responsive system UI and stable Service Level Objectives (SLOs), this repository optimizes for two distinct performance tiers based on your concurrency needs.

## 🚀 Tier 1: Multi-Agent Optimal (8B–11B)
**Best for**: Running 3–5 concurrent agents (OpenClaw, ZeroClaw, OpenFang) without memory trashing. These models provide sub-second hot-swapping and zero degradation under pressure.

| Model ID (HuggingFace) | Parameters | Format | Recommended Role |
| :--- | :--- | :--- | :--- |
| `mlx-community/Hermes-3-Llama-3.1-8B-4bit` | 8B | Q4 | **Apex Archetype**: Gold standard for agentic steering and tool use. |
| `mlx-community/Qwen2.5-9B-Instruct-4bit` | 9B | Q4 | **Generalist**: Exceptional performance on Chinese/Multi-lingual and coding tasks. |
| `mlx-community/Gemma-4-E4B-it-4bit` | 4.8B | Q4 | **Edge Agent**: Ultra-fast inference with native multimodal support. |

---

## 🧠 Tier 2: High-Reasoning Specialist (14B–35B MoE)
**Best for**: Single-agent tasks requiring deep logical reasoning, complex code generation, or long-chain thought. 
> [!WARNING]
> Running these models under high concurrency (5+ agents) will likely trigger memory trashing once the KV Cache exceeds the reserved 4GB buffer.

| Model ID (HuggingFace) | Parameters | Format | Why it's remarkable... |
| :--- | :--- | :--- | :--- |
| `mlx-community/Qwen3.5-35B-A3B-MoE-4bit` | 35B (3B active) | Q4 | High reasoning with an MoE footprint that fits comfortably in 24GB. |
| `mlx-community/DeepSeek-R1-Distill-Qwen-14B-4bit`| 14B | Q4 | State-of-the-art Chain-of-Thought (CoT) reasoning in a small footprint. |
| `mlx-community/GLM-5-Air-Instruct-4bit` | 9B | Q4 | Highly efficient Chinese OSS leader; superior math and logical grounding. |

---

## 🎭 Hermes Agent Specials (Agentic Tool-Use)
For the **Hermes Agent** framework, we recommend models that utilize Gemma 4's native function-calling architecture combined with Nous Research steering.

| Recommended Model ID (MLX Optimized) | Fit for Hermes Agent... |
| :--- | :--- |
| **`jason-schulz/Gemma-4-26B-A4B-Hermes-VLM-MLX-4bit`** | **The Best Fit**: A weight-graft that combines Gemma 4's native tool-tokens with Hermes-3's persona and memory-handling excellence. |
| `mlx-community/Gemma-4-31B-Dense-4bit` | Dense-power alternative for when MoE routing jitter is unacceptable. |

---

## 🔧 Deployment Summary
- **Primary Engine**: `mlx-lm` (via Go substrate).
- **VRAM Safety Zone**: Keep weight-loading + KV Cache below **22GB** to avoid kernel UI freezes.
- **Hot-Swap Latency**: Sub-5s for Tier 1; ~15s–30s for Tier 2.

> [!TIP]
> Use `uv run event-horizon pull <ModelID>` to pre-download any model from the list above before starting a multi-agent session.
