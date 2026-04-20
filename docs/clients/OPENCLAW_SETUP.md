# OpenClaw Setup

This guide explains how to connect the **OpenClaw** agentic framework to the **Event Horizon Core** Go Substrate.

## Connection Details

OpenClaw is optimized for the OpenAI-compatible API provided by the Event Horizon Core background daemon.

### 1. Identify your local endpoint
By default, the core uses:
- **URL**: `http://localhost:8000/v1`
- **API Key**: `sk-antigravity` (Any string works)

### 2. Configure OpenClaw
Update your `openclaw/config.yaml` or `.env`:

```env
OPENAI_API_BASE=http://localhost:8000/v1
OPENAI_API_KEY=sk-antigravity
MODEL=mlx-community/Hermes-4-Llama-3.1-8B-4bit
```

## Recommended Models

For **OpenClaw (Autonomous Logic)**:
- `mlx-community/Hermes-4-Llama-3.1-8B-4bit` (Apex tool-use precision)
- `mlx-community/Qwen3.5-9B-Instruct-4bit` (Best generalist for multiturn chat)

## Event Horizon Core Requirements
To properly interface with the Event Horizon orchestration substrate, this client **MUST** inject the `X-Agent-Name` HTTP header into all `/v1/chat/completions` API requests.
Failure to provide this header will trigger server-side warnings and eventually firewall interception.

Example: `X-Agent-Name: openclaw`
