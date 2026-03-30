# LLM Model Candidates (Local Analytics)

This document contains a curated list of top LLM candidates for local deployment on Apple Silicon, analyzed via the `llmfit` utility. 

## Column Definitions

- **Model**: The HuggingFace repository or model name.
- **Params**: Total parameter count (e.g., 8B, 70B). Higher counts generally mean better reasoning but higher memory requirements.
- **Quant**: Quantization level (e.g., Q4_K_M). This reduces model size and memory usage by compressing weights.
- **Mem (RAM/VRAM)**: The minimum estimated memory required to load the model. (RAM for System, VRAM for Apple Silicon Unified Memory/GPU).
- **tok/s**: Estimated tokens per second on current hardware (Calculated based on local benchmarks).
- **Context**: The maximum context window (input tokens) the model can handle (e.g., 32k, 128k).
- **Format**: The file format (GGUF for Ollama/LLama.cpp, MLX for Native).

## Top Candidate Table

| Model | Params | Quant | Mem (RAM/VRAM) | tok/s | Context | Format |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **mlx-community/Llama-3.2-3B-Instruct-4bit** | 3.2B | 4-bit | 2.5G/1.8G | ~85 | 128k | MLX |
| **llama3.1:8b-instruct-q4_K_M** | 8.0B | Q4_K_M | 5.2G/4.8G | ~45 | 128k | GGUF |
| **mistral-7b-v0.3:q4_K_M** | 7.2B | Q4_K_M | 4.8G/4.2G | ~52 | 32k | GGUF |
| **qwen2.5-7b-instruct-q4_K_M** | 7.6B | Q4_K_M | 5.0G/4.5G | ~48 | 128k | GGUF |
| **phi-3.5-mini-instruct:q4_K_M** | 3.8B | Q4_K_M | 2.8G/2.2G | ~92 | 128k | GGUF |
| **gemma-2-9b-it-q4_K_M** | 9.2B | Q4_K_M | 6.5G/5.8G | ~38 | 8k | GGUF |
| **deepseek-v3:q4_K_M** | 685B | Q4_K_M | 383G/351G | <1 | 128k | GGUF |
| **Llama-3.3-70B-Instruct-Q4_K_M** | 70B | Q4_K_M | 42G/38G | ~12 | 128k | GGUF |
| **allenai/Olmo-3-7B-Think** | 7B | Q4_K_M | 4.8G/4.2G | ~50 | 64k | GGUF |
| **tiny-random/qwen3-next-moe** | 3M | Q4_K_M | 1.0G/0.5G | >200 | 256k | GGUF |

---
**Note**: Benchmarks are estimated based on Apple Silicon (Unified Memory) architecture using `llmfit` scoring heuristics.
