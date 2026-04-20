# 🌌 Event Horizon Core: Cheat Sheet

This guide covers monitoring the Go Daemon (Substrate) and the underlying MLX Inference Engine.

---

## 🚀 The Core Gateway (Port 8000)
*Recommended method for all interaction.*

### Check Health Status
```bash
# Via Python thin-client
uv run event-horizon status

# Via shorthand alias
uv run event-horizon mlx

# Via raw cURL
curl http://127.0.0.1:8000/status
```

### Available Models (MLX)
To enumerate all MLX models currently downloaded and cached on your machine:
```bash
# List all directories in the HuggingFace hub cache
ls -d ~/.cache/huggingface/hub/models--* | sed 's|.*/models--||;s|--|/|'
```

### Downloading Models
Models are automatically downloaded when first requested via the `generate` command. To manually pre-download a model:
```bash
# Using the project Python environment
uv run python -m mlx_lm.download --model "org/repo"

# Example
uv run python -m mlx_lm.download --model "mlx-community/Llama-3.2-3B-Instruct-4bit"
```

### Perform Inference
```bash
# Tier 1: Local MLX (Auto-swaps model on M5 VRAM)
uv run event-horizon generate "Hello World" --model "mlx-community/Llama-3.2-3B-Instruct-4bit"

# Tier 2: Zero-Cost Remote (Gemini Flash Exp)
uv run event-horizon generate "Refactor this Go code" --model "free"
```

### Offloading Models
To delete downloaded models and free up storage space, remove them from the HuggingFace cache:
```bash
# Interactively select models to delete (if huggingface-cli is installed)
uv run huggingface-cli delete-cache

# Or manually remove a specific model folder found in ~/.cache/huggingface/hub
# rm -rf ~/.cache/huggingface/hub/models--org--repo
```

---

## 🛠️ macOS Service Management (Persistence)
Use these when troubleshooting the background daemon.

### Restart/Reload Service
```bash
# Unload and Reload (Refreshes config/binary)
launchctl unload ~/Library/LaunchAgents/com.antigravity.eventhorizon.plist
launchctl load ~/Library/LaunchAgents/com.antigravity.eventhorizon.plist
```

### View Live Logs
```bash
# Follow Go Daemon & MLX Supervisor output
tail -f ~/antigravity/event-horizon-core/daemon.log
```

---

## 🔍 Low-Level Diagnostics
Use these if the daemon says the supervisor is "stopped."

### Check Process Ownership
```bash
# See the Go Daemon
ps aux | grep event-horizon

# See the Supervised Inference Engine
ps aux | grep mlx_lm.server
```

### Direct Hardware Test (Bypass Proxy)
```bash
# Test Port 8080 directly to verify Metal/ANE health
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "default", "messages": [{"role": "user", "content": "Proof of life"}]}'
```

---

## 💸 VRAM Management
*   **Capacity**: 24GB Unified Memory (M5).
*   **Safe Zone**: Keep model parameters **< 15B**.
*   **Purge**: If VRAM is full and processes are stuck:
    `pkill -9 -f mlx_lm.server && pkill -9 event-horizon` (macOS will restart them clean).
