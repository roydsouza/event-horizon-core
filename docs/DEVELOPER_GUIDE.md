# Event Horizon Core: Developer Guide

This guide describes how to extend and maintain the `event-horizon-core` package.

## Architecture Architecture

`event-horizon-core` follows a simple **Factory Pattern**:

1.  **Providers** (`event_horizon_core/providers/`): Implement the `BaseLLMProvider` interface.
2.  **Factory** (`event_horizon_core/factory.py`): Manages the registration and instantiation of providers.
3.  **CLI** (`event_horizon_core/cli.py`): Provides a unified user interface.

## Adding a New Provider

To add a new LLM backend (e.g., `llama.cpp`, `vllm`):

1.  **Create the Provider File**:
    In `event_horizon_core/providers/`, create `new_provider.py`. Inherit from `BaseLLMProvider`.

    ```python
    from .base import BaseLLMProvider
    
    class NewProvider(BaseLLMProvider):
        def generate(self, prompt, system_prompt=None, **kwargs):
            # Implementation here
            return "response"
        
        def is_healthy(self) -> bool:
            return True
    ```

2.  **Register with the Factory**:
    In `event_horizon_core/factory.py`, import your new provider and add it to the `PROVIDERS` dictionary.

    ```python
    from .providers.new_provider import NewProvider
    
    PROVIDERS = {
        "new": NewProvider,
        # ...
    }
    ```

## VRAM Calculation

The `MLXProvider` implements a `get_vram_estimate()` method. When adding new local providers, ensure you include memory safety checks to prevent crashing the OS on your 24GB M5.

## Testing

Run tests from the root directory:

```bash
pytest tests/
```

Individual provider tests:
```bash
pytest tests/test_mlx.py
```
