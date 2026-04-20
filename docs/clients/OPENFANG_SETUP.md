# OpenFang Agent Setup

This guide covers connecting the high-performance **OpenFang** agent to the **Event Horizon Core** Go Substrate.

## OpenFang Agent Overview

OpenFang is specialized for safety and security audits. It requires a robust local backend for low-latency inference.

- **Recommended Model**: OpenFang works best with **Qwen3.5-9B-Instruct**.

## Setup Instructions

### 1. Identify Connection Details
Point OpenFang to the local core endpoint:
- **URL**: `http://localhost:8000/v1`
- **API Key**: `sk-antigravity`

### 2. Configuration Example
Update your agent configuration (e.g., `config.yaml`):

```yaml
agent:
  name: "OpenFang"
  provider: "openai"
  model: "mlx-community/Qwen3.5-9B-Instruct-4bit"
  base_url: "http://localhost:8000/v1"
```

## Event Horizon Core Requirements
To properly interface with the Event Horizon orchestration substrate, this client **MUST** inject the `X-Agent-Name` HTTP header into all `/v1/chat/completions` API requests.
Failure to provide this header will trigger server-side warnings and eventually firewall interception.

Example: `X-Agent-Name: openfang`
