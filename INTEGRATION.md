# 🔌 Event Horizon Integration Guide

This document provides technical specifications for integrating **AntiGravity** agents (OpenClaw, ZeroClaw, OpenFang, Hermes, Tachyon Tongs) with the **Event Horizon Core** Go Substrate.

## 🚀 Transparent Compatibility (OpenAI Standard)

Event Horizon Core is designed to be **drop-in compatible** with any client that supports the **OpenAI API Standard**. It acts as a high-performance proxy on Port `8000`.

### 🛣️ Endpoints
- **Chat Completions**: `http://127.0.0.1:8000/v1/chat/completions` (OpenAI Compatible)
- **Status/Health**: `http://127.0.0.1:8000/status`

---

## 🛠️ Integration Mapping for Common Clients

### 1. Clients expecting OpenAI (e.g., Hermes, ZeroClaw)
Most agents expect `OPENAI_BASE_URL` and `OPENAI_API_KEY`.

**Configuration:**
- `OPENAI_BASE_URL="http://127.0.0.1:8000/v1"`
- `OPENAI_API_KEY="sk-antigravity"` (Any non-empty string works for local MLX)

### 2. Clients expecting Ollama (e.g., legacy scripts)
Event Horizon does **not** spoof the `/api/generate` Ollama-specific endpoint.

**Modification Needed:**
- Update the client to use the `openai` provider instead of `ollama`.
- Point the base URL to `http://127.0.0.1:8000/v1`.

### 3. Clients expecting OpenRouter (e.g., OpenClaw, Tachyon Tongs)
Event Horizon handles inference **locally**. You do NOT need to configure the client to talk to OpenRouter directly.

**Configuration:**
- Point the client to Event Horizon (`http://127.0.0.1:8000/v1`).
- Set the `model` to a specific MLX HuggingFace path (e.g. `mlx-community/Llama-3.1-8B-Instruct-4bit`).
- The Go substrate will automatically detect if the model should be hot-swapped locally.

---

## 🧠 Model Selection Logic

### 1. Explicit Model Injection
Agents must provide a valid **HuggingFace path** that supports MLX in the standard `model` field.

| Type | Target Model | Best For... |
| :--- | :--- | :--- |
| **Logic/Draft** | `mlx-community/Llama-3.2-3B-Instruct-4bit` | Fast background tasks & reflection. |
| **Reasoning** | `mlx-community/Llama-3.1-8B-Instruct-4bit` | General intelligence & tool-use. |
| **Coding** | `mlx-community/Qwen2.5-7B-Instruct-4bit` | High intelligence/logic in 7B range. |

### 2. Automatic Hot-Swapping
The substrate will automatically detect if the requested model differs from the one currently loaded in VRAM. It will gracefully bounce the server to load the new weights while blocking the client connection to prevent 502 errors.

---

## 🧪 Quick Test (cURL)

To verify a client's ability to connect before deployment:

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mlx-community/Llama-3.2-3B-Instruct-4bit",
    "messages": [{"role": "user", "content": "Hello Core"}]
  }'
```

## ⚠️ AntiGravity Deployment Note
When AntiGravity installs a new agent, it MUST:
1. Ensure the `event-horizon` daemon is running (`launchctl list | grep eventhorizon`).
2. Inject `EVENT_HORIZON_URL="http://127.0.0.1:8000/v1"` into the agent's `.env`.
3. Set the agent's default `MODEL_ID` to a validated local MLX path.
