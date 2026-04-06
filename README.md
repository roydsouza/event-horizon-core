# 🌌 Event Horizon Core

**Event Horizon Core** is a high-performance, local-only orchestration layer for LLM inference, specifically engineered for **Apple Silicon (M5)** hardware. It provides a highly efficient Go substrate to manage local Metal VRAM and coordinate multi-agent workflows with zero external dependencies.

## 💻 CLI Usage (Direct Access)

The high-speed Python thin-client proxies all inference to the background Go Daemon (Port 8000).

```bash
# Check status (Verifies M5 Metal & Supervisor health)
uv run event-horizon status

# Generate with local MLX
# Auto-swaps model if requester mismatch detected.
uv run event-horizon generate "Your prompt" --model "mlx-community/Hermes-3-Llama-3.1-8B-4bit"

# Check MLX status specifically
uv run event-horizon mlx
```

## 🏠 Local-First Inference (24GB M5 Optimized)

Event Horizon is a "Local Only" manager, prioritizing the privacy and performance of your M5 hardware. For 24GB Unified Memory, we recommend staying under ~15B parameters for 4-bit quantized models to ensure 100% OS stability during multi-agent saturation.

**Recommended Local Models (HuggingFace MLX):**
*   `mlx-community/Hermes-3-Llama-3.1-8B-4bit` (Apex reasoning, balanced speed)
*   `mlx-community/Llama-3.2-3B-Instruct-4bit` (Ultra-fast, fit for background agents)
*   `mlx-community/Mistral-7B-Instruct-v0.3-4bit` (Great for function calling)

### 🔧 Explicit Model Control
Provide any valid **HuggingFace path** that supports MLX. 

**Examples:**
- `uv run event-horizon generate "..." --model "mlx-community/Qwen2.5-7B-Instruct-4bit"`
- `uv run event-horizon generate "..." --model "mlx-community/Llama-3.2-3B-Instruct"`

---

## 🚀 Key Features (M5-Native)

*   **Go Daemon Substrate**: Zero-dependency Go background service for minimal memory footprint and hardened security.
*   **Active Supervision**: Subprocess management with **Anti-Zombie Mutex** (Process Groups) ensures 0 VRAM leaks.
*   **Dynamic Model Swapping**: Hot-swap MLX models on-the-fly with blocking HTTP middleware.
*   **Hardware Optimizations**: Native support for **Prefix Caching** and **Speculative Decoding**.
*   **macOS Persistence**: Integrated `launchd` service for invisible, self-healing operation.

## 🏗 Architecture

*   `cmd/event-horizon`: Daemon entry point.
*   `internal/supervisor`: Process lifecycle and anti-zombie logic.
*   `internal/server`: HTTP routing and hot-swap middleware.
*   `event_horizon_core/`: Python thin-client implementation.

## 📜 License
Part of the AntiGravity research series. All rights reserved.

---

## 🚦 Operational Guardrails & SLOs

The **Event Horizon Core** is engineered for high-concurrency agentic workloads on Apple Silicon M5 (24GB). Based on hardware-native benchmarks, we maintain the following **Service Level Objectives (SLOs)**:

| Metric | SLO (Target) | Observed (M5-24GB) | Notes |
| :--- | :--- | :--- | :--- |
| **Availability** | 99.9% | 100% | Self-healing Go supervisor kills zombies. |
| **TTFT (Warm)** | < 1.0s | **0.74s** (P95) | MLX Prefix Caching is active. |
| **Hot-Swap** | < 3.0s | **1.93s** (Max) | 3B $\leftrightarrow$ 1B weight swap latency. |
| **Throughput** | > 20 tok/s | **21.8 tok/s** | Under 10-client concurrent load. |

### Performance Isolation
To maintain these SLOs, the Go substrate enforces:
- **VRAM Guard**: Hard cap at 22GB to prevent OS-level swapping/beachballing.
- **Process Group Isolation**: Guarantees zero orphan servers after a "Model Swap."
- **Continuous Batching**: Natively handled by the underlying MLX implementation.

### Reproducing Benchmarks
You can verify these metrics on your local machine using the hardware integrity suite:
```bash
uv run python3 tests/hardware_benchmark.py
```

### System Load Monitoring (Apple Silicon)
To monitor the true impact of the LLM substrates across your Unified Memory (VRAM), Neural Engine, and GPU, use `asitop`:

1. **Install metrics tool** (global `uv` toolchain):
   ```bash
   uv tool install asitop
   ```
2. **Launch real-time monitor**:
   ```bash
   sudo asitop
   ```
   *(Note: macOS requires `sudo` privileges to poll the internal `powermetrics` hardware sensors used by asitop).*
