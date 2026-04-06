# 📖 Supported Models (M5 24GB Optimized)

> [!CAUTION] 
> **Hardware Boundary Limitations (M5 24GB)**
> Following comprehensive multi-agent concurrency benchmarking across the core substrate, we've definitively established that 32B-parameter models cause catastrophic memory trashing under load on Apple Silicon 24GB machines. To protect Service Level Objectives (SLOs), this repository natively optimizes for the **8B-14B parameter** classes—with `Hermes-3-Llama-3.1-8B` serving as the apex archetype.
> 
> *For the complete empirical latency tables and the formal stress test overview that drove this optimization, please reference the full **[LLM Stress Test Results](TEST_RESULTS.md)***.

This document lists the **local-only** models specifically curated for the **Apple Silicon M5 (24GB Unified Memory)** using the MLX framework.

## 🏠 Local Models (Native MLX)
These models run directly on your GPU. For 24GB VRAM, we prioritize 4-bit (Q4) or 8-bit (Q8) quantized models under 15B parameters to maintain system responsiveness during multi-agent workflows.

| Model ID (HuggingFace) | Parameters | Format | Best For... |
| :--- | :--- | :--- | :--- |
| `mlx-community/Llama-3.2-1B-Instruct-4bit` | 1B | Q4 | Ultra-fast reflection, drafting, and tool-triggering. |
| `mlx-community/Llama-3.2-3B-Instruct-4bit` | 3B | Q4 | Background agents, summarization, and simple chat. |
| `mlx-community/Llama-3.1-8B-Instruct-4bit` | 8B | Q4 | General purpose reasoning, coding, and instruction following. |
| `mlx-community/Mistral-7B-Instruct-v0.3-4bit`| 7B | Q4 | Function calling and creative writing. |
| `mlx-community/Qwen2.5-7B-Instruct-4bit` | 7B | Q4 | High intelligence in a small footprint. |

> [!IMPORTANT]
> **VRAM Safety Zone**: On a 24GB M5, sticking to models <15B ensures that your OS UI remains fluid even during peak multi-agent inference.

---

## 🔧 Explicit Model Control
You are not limited to this list. You can provide **any** valid HuggingFace Model ID that supports MLX to the `generate` command.

**Examples:**
- `uv run event-horizon generate "..." --model "mlx-community/DeepSeek-V3-MLX"` (If VRAM allows)
- `uv run event-horizon generate "..." --model "mlx-community/Llama-3.2-3B-Instruct"`

---
