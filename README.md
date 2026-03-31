# 🌌 Event Horizon Core

**Event Horizon Core** is a high-performance orchestration layer for LLM inference, specifically engineered for **Apple Silicon (M5)** hardware. It manages local Metal VRAM efficiently and provides a seamless fallback hierarchy for multi-agent workflows.

## 🚀 Key Features (M5-Native)

*   **Go Daemon Substrate**: Zero-dependency Go background service for minimal memory footprint and maximum concurrency.
*   **Active Supervision**: Subprocess management with **Anti-Zombie Mutex** (Process Groups) ensures 0 VRAM leaks.
*   **Dynamic Model Swapping**: Hot-swap MLX models on-the-fly with blocking HTTP middleware (No 502/504 errors).
*   **Hardware Optimizations**: Native support for **Prefix Caching** (`--prompt-cache-size`) and **Speculative Decoding** (`--draft-model`).
*   **Tiered Fallback Hierarchy**:
    1.  **Tier 1 (Local)**: MLX (`mlx_lm.server`)
    2.  **Tier 2 (Fallback)**: Llama.cpp (`llama-server`)
    3.  **Tier 3 (Remote)**: OpenRouter (Claude, Gemini, Llama 3)
*   **macOS Persistence**: Integrated `launchd` service for invisible, self-healing background operation.

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
