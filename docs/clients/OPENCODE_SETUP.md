# OpenCode Setup

OpenCode is an IDE-integrated agent and requires a high-performance local backend for real-time suggestions.

## Configuration

To hook up OpenCode to use the **Event Horizon Core** Go Substrate:

```yaml
# config.yaml
llm:
  provider: "openai"
  api_base: "http://localhost:8000/v1"
  api_key: "sk-antigravity"
  model: "mlx-community/Qwen3.5-9B-Instruct-4bit"
```

## CLI Performance Validation

Test the coding speed on your M5:

```bash
event-horizon generate "Write a python script to parse logs" --model "mlx-community/Qwen3.5-9B-Instruct-4bit"
```

> [!TIP]
> For complex logic or architectural planning sessions, swap to **`mlx-community/DeepSeek-R1-Distill-Qwen-14B-4bit`** for state-of-the-art local reasoning.


## Event Horizon Core Requirements
To properly interface with the Event Horizon orchestration substrate, this client **MUST** inject the `X-Agent-Name` HTTP header into all `/v1/chat/completions` API requests.
Failure to provide this header will trigger server-side warnings and eventually firewall interception.

Example: `X-Agent-Name: opencode`
