# Hermes Agent Setup

This guide covers connecting the autonomous **Hermes** agent to the **Event Horizon Core** Go Substrate.

## Hermes Agent Overview

Hermes is specialized in complex reasoning and long-term task management. It requires high accuracy in tool use for optimal performance.

- **Recommended Model**: Use **Gemma-4-26B-A4B-Hermes** (MoE) for high-intelligence logic or **Hermes-4-8B** for a faster mission profile.

## Setup Instructions

### 1. Test Tool Call Ability
Validate that the core can handle tool calls with the selected model:
```bash
event-horizon generate "Run this tool..." --model "jason-schulz/Gemma-4-26B-A4B-Hermes-VLM-MLX-4bit" --temp 0.0
```

### 2. Configure Hermes
Update your `hermes/config.json` to point to the local core endpoint:

```json
{
  "model": "jason-schulz/Gemma-4-26B-A4B-Hermes-VLM-MLX-4bit",
  "api_base": "http://localhost:8000/v1"
}
```

## Event Horizon Core Requirements
To properly interface with the Event Horizon orchestration substrate, this client **MUST** inject the `X-Agent-Name` HTTP header into all `/v1/chat/completions` API requests.
Failure to provide this header will trigger server-side warnings and eventually firewall interception.

Example: `X-Agent-Name: hermes`
