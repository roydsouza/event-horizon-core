# OpenFang & Hermes Agent Setup

These guides cover connecting the more advanced **OpenFang** and **Hermes** agents to the `event-horizon-core`.

## OpenFang Setup

OpenFang is a high-performance agent for safety and security audits. It requires a robust local backend.

1.  **Select a Model**: OpenFang works best with **Llama-3.1-8B** or **Mistral Nemo**.
2.  **Point to the Core Endpoint**:
    - **URL**: `http://localhost:11434/v1`
    - **Provider**: `ollama`

### Configuration Example
```yaml
agent:
  name: "OpenFang"
  provider: "ollama"
  model: "llama3.1"
  base_url: "http://localhost:11434/v1"
```

## Hermes Agent Setup

Hermes is an autonomous agent specialized in complex reasoning and long-term task management.

- **Requirements**: High accuracy in tool use. Use **Llama-3.1-8B** or **Llama-3.3-70B** (via OpenRouter).

### Setup Loop
1.  **Test Tool Call Ability**:
    ```bash
    event-horizon generate ollama "Run this tool..." --model llama3.1 --temp 0.0
    ```
2.  **Integrate**:
    Update `hermes/config.json`:
    ```json
    {
      "model": "llama3.1",
      "api_base": "http://localhost:11434/v1"
    }
    ```
