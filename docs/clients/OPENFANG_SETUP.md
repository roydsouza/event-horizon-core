# OpenFang & Hermes Agent Setup

These guides cover connecting the more advanced **OpenFang** and **Hermes** agents to the **Event Horizon Core** Go Substrate.

## OpenFang Setup

OpenFang is a high-performance agent for safety and security audits. It requires a robust local backend.

1.  **Select a Model**: OpenFang works best with **Llama-3.1-8B-Instruct**.
2.  **Point to the Core Endpoint**:
    - **URL**: `http://localhost:8000/v1`
    - **API Key**: `sk-antigravity`

### Configuration Example
```yaml
agent:
  name: "OpenFang"
  provider: "openai"
  model: "mlx-community/Llama-3.1-8B-Instruct-4bit"
  base_url: "http://localhost:8000/v1"
```

## Hermes Agent Setup

Hermes is an autonomous agent specialized in complex reasoning and long-term task management.

- **Requirements**: High accuracy in tool use. Use **Llama-3.1-8B** for a balanced local mission profile.

### Setup Loop
1.  **Test Tool Call Ability**:
    ```bash
    event-horizon generate "Run this tool..." --model "mlx-community/Llama-3.1-8B-Instruct-4bit" --temp 0.0
    ```
2.  **Integrate**:
    Update `hermes/config.json`:
    ```json
    {
      "model": "mlx-community/Llama-3.1-8B-Instruct-4bit",
      "api_base": "http://localhost:8000/v1"
    }
    ```
