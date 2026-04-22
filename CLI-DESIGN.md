# CLI Design: Event Horizon Core (EHC) v2.0

This document outlines the expanded CLI design for EHC to support multi-engine orchestration and model management.

## 🌌 Core Philosophy
The EHC CLI is a high-speed, thin-client proxy to the Go Substrate. It handles the "Physics of Inference"—managing VRAM, process lifecycles, and engine health—so the operator only needs to care about the prompt.

---

## 🛠️ Command Reference

### 1. `generate` (The Orchestrator)
The primary command for text generation. It is **coordinated**, meaning it will automatically trigger hardware reconfigurations (swaps) if needed.

**Usage:**
```bash
event-horizon generate "Your prompt" [OPTIONS]
```

**Options:**
- `--engine`: (Default: `mlx-lm`) Selection: `bodega`, `vllm`, `mlx-lm`.
- `--model`: (Default: `active`) Any valid local HuggingFace path.
- `--temp`: (Default: `0.7`) Sampling temperature.
- `--max-tokens`: (Default: `500`).

**🔄 Lifecycle of a Generate Call:**
1.  **Intercept**: Go Daemon receives the request and checks the active VRAM state.
2.  **Verify**: Ensures requested engine and model are available on disk.
3.  **Swap (if needed)**: If active hardware state != requested state:
    *   **SIGKILL** current engine process group (instant memory release).
    *   **Launch** new engine/model pair.
    *   **Health Check**: Polls until the engine is warm.
4.  **Forward**: Proxies the prompt to the now-warm backend.
5.  **Stream**: Returns the generated tokens to the CLI.

---

### 2. `engines` (Infrastructure Management)
Manages the various inference backends available to the station.

**Commands:**
- `engines --list`: Shows all supported engines, their installation status, and which one is currently `[ACTIVE]`.
- `engines --check`: Runs a health check on all installed engines to verify Metal/NPU accessibility.

**Example Output:**
```
[*] mlx-lm   [ACTIVE]   (Native MLX implementation)
[*] bodega   [READY]    (High-performance agentic engine)
[*] vllm     [READY]    (Throughput-optimized serving)
```

---

### 3. `models` (VRAM Asset Management)
Controls the local model cache and asset ingestion.

**Commands:**
- `models --list`: Scans `~/.cache/huggingface` and lists models quantized for Apple Silicon. Shows model size and compatibility tags (e.g., `[MLX]`, `[GGUF]`).
- `models --download <HF_ID>`: Ingests a new model from HuggingFace. Automatically selects the 4-bit MLX-community quantization if available.
- `models --evict <HF_ID>`: Safely removes a model from the local cache.

---

## 🏗️ Technical Implementation

### Go Substrate (The Dispatcher)
The Go daemon acts as the "Engine Dispatcher":
1.  **Validation**: Checks if the requested engine is in the `$PATH`.
2.  **Isolation**: Each engine is run in its own Process Group (`Setpgid: true`) to ensure no "zombie" servers remain after a swap.
3.  **Unified API**: Go maps the request to the specific CLI flags needed by the target engine (e.g., `--model` for MLX vs `-m` for llama.cpp).

---

## 📅 Roadmap for Implementation

1.  **Phase 1**: Define the `Engine` interface in Go.
2.  **Phase 2**: Update `HandleCompletions` to support the `engine` parameter.
3.  **Phase 3**: Overhaul `event_horizon_core/cli.py` with the new command groups.
4.  **Phase 4**: Implement `models --download` using `huggingface_hub`.
