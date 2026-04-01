# 🌌 Event Horizon Core

**Event Horizon Core** is a high-performance orchestration layer for LLM inference, specifically engineered for **Apple Silicon (M5)** hardware. It manages local Metal VRAM efficiently and provides a seamless fallback hierarchy for multi-agent workflows.

## 🚀 Key Features (M5-Native)

*   **Go Daemon Substrate**: Zero-dependency Go background service for minimal memory footprint and maximum concurrency.
*   **Active Supervision**: Subprocess management with **Anti-Zombie Mutex** (Process Groups) ensures 0 VRAM leaks.
*   **Dynamic Model Swapping**: Hot-swap MLX models on-the-fly with blocking HTTP middleware (No 502/504 errors).
*   **Hardware Optimizations**: Native support for **Prefix Caching** (`--prompt-cache-size`) and **Speculative Decoding** (`--draft-model`).
*   **2-Tier Fast Proxy**: 
    1.  **Tier 1 (Local)**: Direct-to-Metal MLX (`mlx_lm.server`).
    2.  **Tier 3 (Remote)**: OpenRouter (Claude, Gemini, Llama 3).
*   **macOS Persistence**: Integrated `launchd` service for invisible, self-healing background operation.

## 💸 Zero-Cost Inference (Free & Local-First)

Event Horizon is optimized for a **Zero-Cost Workflow**, prioritizing your local M5 hardware and free remote providers.

### 🏠 Tier 1: Local (24GB M5 Optimized)
These models run natively on your Metal GPU using MLX. For your 24GB Unified Memory, stay under ~15B parameters for 4-bit quantized models to ensure 100% OS stability.

**Recommended Free Local Models:**
*   `mlx-community/Llama-3.2-3B-Instruct-4bit` (Ultra-fast, fit for background agents)
*   `mlx-community/Llama-3.1-8B-Instruct-4bit` (Balanced logic/speed)
*   `mlx-community/Mistral-7B-Instruct-v0.3-4bit` (Great for function calling)

### ☁️ Tier 3: Free Remote Fallbacks (OpenRouter)
When you need high intelligence without VRAM/Electricity cost, use these free aliases:

| Label | Target Model (OpenRouter) | Note |
| :--- | :--- | :--- |
| **`free`** | `google/gemini-2.0-flash-exp:free` | **Primary Choice.** Unlimited context, multimodal, zero cost. |
| **`fast`** | `google/gemini-2.0-flash-001` | Extremely fast (small credit usage if exp is busy). |

> [!TIP]
> Use the **`free`** label for your "grunt work" agents to keep your M5 focused on local inference while leveraging Gemini Flash for zero cost.

## 🛠 Installation & Setup

1.  **Clone & Go Build**:
    ```bash
    go build -o event-horizon ./cmd/event-horizon
    ```

2.  **macOS Service Activation**:
    ```bash
    # Copy the plist to your LaunchAgents
    cp build/com.antigravity.eventhorizon.plist ~/Library/LaunchAgents/
    # Load the service
    launchctl load ~/Library/LaunchAgents/com.antigravity.eventhorizon.plist
    ```

3.  **Python thin-Client**:
    ```bash
    uv sync
    uv run event-horizon status
    ```

## 💻 CLI Usage

The Python CLI now acts as a high-speed thin client proxying to the Go Daemon (Port 8000).

```bash
# Check status and loaded models
uv run event-horizon status

# Generate with local MLX (Autoswaps model if needed)
uv run event-horizon generate "Your prompt" --model "mlx-community/Llama-3.2-3B-Instruct-4bit"

# Generate with remote fallback (Using Aliases)
uv run event-horizon generate "Explain PQC" --model "best"
```

## 🏗 Architecture

*   `cmd/event-horizon`: Daemon entry point.
*   `internal/supervisor`: Process lifecycle and anti-zombie logic.
*   `internal/server`: HTTP routing and hot-swap middleware.
*   `internal/providers`: Remote engine interfaces (OpenRouter).
*   `event_horizon_core/`: Python thin-client implementation.

## 📜 License
Part of the AntiGravity research series. All rights reserved.
