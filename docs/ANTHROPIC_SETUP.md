# Anthropic Integration: Event Horizon Core

This guide explains how to use the centralized **Event Horizon Core** inference engine from within your `~/anthropic` projects.

## 🚀 The Unified Interface (OpenAI Compatible)

The Event Horizon Core Go Daemon (Port 8000) provides a drop-in compatible OpenAI endpoint for all local MLX models. Projects no longer need to import Python logic from the core; they simply treat it as a remote LLM API that happens to be running on localhost.

## Setup Instructions (Python)

### 1. Requirements
Ensure your project has `requests` or the `openai` Python library installed.

### 2. Integration via OpenAI SDK (Recommended)
This is the most robust way to interact with the local MLX models.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="sk-antigravity"  # Placeholder key
)

response = client.chat.completions.create(
    model="mlx-community/Llama-3.2-3B-Instruct-4bit",
    messages=[{"role": "user", "content": "Hello from your agent"}]
)

print(response.choices[0].message.content)
```

### 3. Integration via standard `requests`
For zero-dependency lightweight scripts:

```python
import requests

payload = {
    "model": "mlx-community/Llama-3.2-3B-Instruct-4bit",
    "messages": [{"role": "user", "content": "Explain quantum entanglement."}]
}

resp = requests.post("http://127.0.0.1:8000/v1/chat/completions", json=payload)
print(resp.json()["choices"][0]["message"]["content"])
```

## 🛠️ CLI Interop
If you need to trigger inference from the shell within your project:

```bash
# Verify the daemon is healthy
event-horizon status

# Generate directly
event-horizon generate "Your prompt" --model "mlx-community/Llama-3.1-8B-Instruct-4bit"
```

## ⚠️ Important: VRAM Awareness
When multiple agents from different `~/anthropic` projects request different models, the Go substrate will perform a **Hot-Swap**. This adds roughly 3-5 seconds of latency to the first request while the weights are reloaded into Metal. Sticking to a common model across projects (e.g. Llama-3.1-8B) will eliminate this latency.
