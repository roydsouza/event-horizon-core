import click
import json
import logging
import sys
from .factory import LLMFactory

@click.group()
def main():
    """Event Horizon Core: Unified Local LLM CLI"""
    logging.basicConfig(level=logging.INFO)

@main.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def status(format):
    """Check the status of all local LLM providers."""
    results = LLMFactory.list_all_models()
    
    if format == "json":
        click.echo(json.dumps(results, indent=2))
        return

    click.echo("--- Event Horizon Core Status ---")
    for provider, models in results.items():
        if isinstance(models, list):
            click.echo(f"[*] {provider.upper()}: Online ({len(models)} models)")
            for model in models:
                click.echo(f"    - {model}")
        else:
            click.echo(f"[!] {provider.upper()}: {models}")

@main.command()
@click.argument("provider")
@click.argument("prompt")
@click.option("--system", help="System prompt")
@click.option("--model", help="Specific model to use")
@click.option("--max-tokens", default=500, help="Max tokens to generate")
def generate(provider, prompt, system, model, max_tokens):
    """Generate text using a specific provider."""
    try:
        kwargs = {"max_tokens": max_tokens}
        if model:
            if provider == "mlx":
                kwargs["model_path"] = model
            else:
                kwargs["model"] = model
        
        engine = LLMFactory.get_provider(provider, **kwargs)
        click.echo(f"[*] Querying {provider}...")
        response = engine.generate(prompt, system_prompt=system)
        click.echo("\n--- Response ---")
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
