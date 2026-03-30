# OpenClaw & ZeroClaw Setup

This guide explains how to connect agentic "claws" to the `event-horizon-core`.

## Using Ollama as the Host

Both OpenClaw and ZeroClaw are optimized for the OpenAI-compatible API. `event-horizon-core` uses Ollama under the hood, which also provides this compatibility.

### 1. Identify your local endpoint
By default, the core uses:
- `http://localhost:11434/v1`

### 2. Configure the Claw
In your `openclaw/config.yaml` or `.env`:

```env
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_API_KEY=ollama # Any string works
MODEL=llama3.1:8b-instruct-q4_K_M
```

## Recommended Models for Agentic Work

For **OpenClaw (Autonomous Logic)**:
- `llama3.1:8b` (Best function calling)
- `mistral-nemo` (128k context)

For **ZeroClaw (Minimalist)**:
- `phi3.5-mini` (Extremely fast on M5)
