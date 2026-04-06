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
  model: "mlx-community/Qwen2.5-7B-Instruct-4bit"
```

## CLI Performance Validation

Test the coding speed on your M5:

```bash
event-horizon generate "Write a python script to parse logs" --model "mlx-community/Qwen2.5-7B-Instruct-4bit"
```
