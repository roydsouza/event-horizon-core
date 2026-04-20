# ZeroClaw Setup

ZeroClaw is a minimalist agentic framework and must be configured to use the **Event Horizon Core** Go proxy.

## Connection Details

ZeroClaw expects an OpenAI-compatible endpoint. Point it directly to the background Go Daemon:

- **Endpoint**: `http://localhost:8000/v1`
- **Model**: `mlx-community/Gemma-4-E4B-it-4bit` (Recommended for hardware-native speed)

## Configuration

Update your `.env` or `config.json` in the ZeroClaw directory:

```env
ZEROCLAW_API_BASE=http://localhost:8000/v1
ZEROCLAW_API_KEY=sk-antigravity
ZEROCLAW_MODEL=mlx-community/Gemma-4-E4B-it-4bit
```

## Local CLI Validation

Test your connection before launching ZeroClaw:

```bash
event-horizon generate "Hello ZeroClaw" --model "mlx-community/Gemma-4-E4B-it-4bit"
```


## Event Horizon Core Requirements
To properly interface with the Event Horizon orchestration substrate, this client **MUST** inject the `X-Agent-Name` HTTP header into all `/v1/chat/completions` API requests.
Failure to provide this header will trigger server-side warnings and eventually firewall interception.

Example: `X-Agent-Name: zeroclaw`
