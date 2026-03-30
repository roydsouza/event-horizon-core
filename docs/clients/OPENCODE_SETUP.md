# OpenCode Setup

OpenCode can use `event-horizon-core` as its local intelligence engine.

## Configuration

To hook up OpenCode to use the core's Ollama provider, update your `~/.config/opencode/config.yaml`:

```yaml
providers:
  ollama:
    base_url: "http://localhost:11434"
    model: "qwen2.5-coder:14b" # Recommended for M5-24GB

profiles:
  ghost:
    provider: "ollama"
    model: "qwen2.5-coder:14b"
```

## Running with the Core CLI

You can also use the `event-horizon` CLI to test prompts before running them in OpenCode:

```bash
event-horizon generate ollama "Write a python script to parse logs" --model qwen2.5-coder:14b
```
