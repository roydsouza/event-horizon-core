# ZeroClaw Setup

ZeroClaw is a minimalist agentic framework and can be configured to use `event-horizon-core` backends.

## Connection Details

ZeroClaw expects an OpenAI-compatible endpoint. Since the core's **Ollama** provider supports this natively, use the following:

- **Endpoint**: `http://localhost:11434/v1`
- **Model**: `llama3.2` (Recommended for speed) or `qwen2.5-coder` (Recommended for code)

## Configuration

Update your `.env` or `config.json` in the ZeroClaw directory:

```env
ZEROCLAW_API_BASE=http://localhost:11434/v1
ZEROCLAW_API_KEY=ollama
ZEROCLAW_MODEL=llama3.2
```

## Local CLI Validation

Test your connection before launching ZeroClaw:

```bash
event-horizon generate ollama "Hello ZeroClaw" --model llama3.2
```
