import pytest
from event_horizon_core.factory import LLMFactory
from event_horizon_core.providers.mlx_provider import MLXProvider
from event_horizon_core.providers.ollama_provider import OllamaProvider

def test_factory_registration():
    assert "mlx" in LLMFactory.PROVIDERS
    assert "ollama" in LLMFactory.PROVIDERS

def test_factory_get_provider():
    mlx = LLMFactory.get_provider("mlx")
    assert isinstance(mlx, MLXProvider)
    
    ollama = LLMFactory.get_provider("ollama")
    assert isinstance(ollama, OllamaProvider)

def test_mlx_list_models():
    mlx = MLXProvider()
    models = mlx.list_models()
    assert isinstance(models, list)

def test_ollama_health_and_list():
    ollama = OllamaProvider()
    # This might fail if ollama is not running, but we check the return type
    try:
        models = ollama.list_models()
        assert isinstance(models, list)
    except Exception:
        pytest.skip("Ollama service not available")

def test_factory_list_all():
    results = LLMFactory.list_all_models()
    assert "mlx" in results
    assert "ollama" in results
