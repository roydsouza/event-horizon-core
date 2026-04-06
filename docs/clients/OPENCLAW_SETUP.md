# OpenClaw & ZeroClaw Setup

This guide explains how to connect agentic "claws" to the **Event Horizon Core** Go Substrate.

## Using the Go Proxy as the Host

Both OpenClaw and ZeroClaw are optimized for the OpenAI-compatible API. The Event Horizon Core provides this via its background daemon.

### 1. Identify your local endpoint
By default, the core uses:
- `http://localhost:8000/v1`

### 2. Configure the Claw
In your `openclaw/config.yaml` or `.env`:

```env
OPENAI_API_BASE=http://localhost:8000/v1
OPENAI_API_KEY=sk-antigravity # Any string works
MODEL=mlx-community/Llama-3.1-8B-Instruct-4bit
```

## Recommended Models for Agentic Work

For **OpenClaw (Autonomous Logic)**:
- `mlx-community/Llama-3.1-8B-Instruct-4bit` (Best function calling)
- `mlx-community/Mistral-7B-Instruct-v0.3-4bit` (Great for tool-use)

For **ZeroClaw (Minimalist)**:
- `mlx-community/Llama-3.2-3B-Instruct-4bit` (Extremely fast on M5)
