import click
import json
import logging
import sys
from .factory import LLMFactory

@click.group()
def main():
    """
    Event Horizon Core: Unified Local LLM CLI. 

    The central engine for managing local (MLX, Ollama) and remote (OpenRouter) 
    inference for agentic frameworks like OpenClaw, ZeroClaw, and OpenCode.
    """
    logging.basicConfig(level=logging.ERROR) # Limit noise by default

@main.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text", help="Output format.")
@click.option("--verbose", is_flag=True, help="Include hardware and version details.")
def status(format, verbose):
    """
    Check the status of all local LLM providers and list available models.

    This command queries both the MLX huggingface cache and the Ollama service to 
    provide a consolidated view of your local intelligence assets.
    """
    results = LLMFactory.list_all_models()
    
    if format == "json":
        click.echo(json.dumps(results, indent=2))
        return

    click.echo("\x1b[1m--- Event Horizon Core Status ---\x1b[0m")
    for provider, models in results.items():
        if isinstance(models, list):
            color = "\x1b[32m" # Green
            click.echo(f"{color}[*] {provider.upper()}\x1b[0m: Online ({len(models)} models)")
            for model in models:
                click.echo(f"    - {model}")
        else:
            color = "\x1b[31m" # Red
            click.echo(f"{color}[!] {provider.upper()}\x1b[0m: {models}")

@main.command()
@click.argument("provider")
@click.argument("prompt")
@click.option("--system", help="Optional system directive to set behavior.")
@click.option("--model", help="Specific model ID (e.g. 'llama3.2' or 'mlx-community/...')")
@click.option("--max-tokens", default=500, type=int, help="Maximum number of tokens to generate.")
@click.option("--temp", default=0.7, type=float, help="Temperature for sampling (0.0 to 1.0).")
@click.option("--json", "json_format", is_flag=True, help="Force output in raw JSON format.")
def generate(provider, prompt, system, model, max_tokens, temp, json_format):
    """
    Generate text using a specific provider (mlx, ollama, or openrouter).

    EXAMPLES:\n
    1. Local MLX (Apple Silicon Native):\n
       event-horizon generate mlx "Write a Rust function" --system "You are a senior coder"\n\n
    2. Ollama (Multi-model support):\n
       event-horizon generate ollama "What is the capital of France?" --model llama3.1\n\n
    3. OpenRouter (Remote fallback):\n
       event-horizon generate openrouter "Complex reasoning..." --model "anthropic/claude-3-opus"
    """
    try:
        kwargs = {"max_tokens": max_tokens, "temperature": temp}
        if model:
            if provider == "mlx":
                kwargs["model_path"] = model
            else:
                kwargs["model"] = model
        
        engine = LLMFactory.get_provider(provider, **kwargs)
        
        if not json_format:
            click.echo(f"\x1b[34m[*] Querying {provider}...\x1b[0m")
        
        response = engine.generate(prompt, system_prompt=system)
        
        if json_format:
            click.echo(json.dumps({"provider": provider, "response": response}, indent=2))
        else:
            click.echo("\n\x1b[1m--- Response ---\x1b[0m")
            click.echo(response)
    except Exception as e:
        click.echo(f"\x1b[31mError:\x1b[0m {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
