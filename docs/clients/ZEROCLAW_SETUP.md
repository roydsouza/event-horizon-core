# ZeroClaw Setup

ZeroClaw is a minimalist agentic framework and must be configured to use the **Event Horizon Core** Go proxy.

## Connection Details

ZeroClaw expects an OpenAI-compatible endpoint. Point it directly to the background Go Daemon:

- **Endpoint**: `http://localhost:8000/v1`
- **Model**: `mlx-community/Llama-3.2-3B-Instruct-4bit` (Recommended for pure speed)

## Configuration

Update your `.env` or `config.json` in the ZeroClaw directory:

```env
ZEROCLAW_API_BASE=http://localhost:8000/v1
ZEROCLAW_API_KEY=sk-antigravity
ZEROCLAW_MODEL=mlx-community/Llama-3.2-3B-Instruct-4bit
```

## Local CLI Validation

Test your connection before launching ZeroClaw:

```bash
event-horizon generate "Hello ZeroClaw" --model "mlx-community/Llama-3.2-3B-Instruct-4bit"
```
