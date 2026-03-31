import asyncio
import click
import json
import logging
import sys
from dotenv import load_dotenv
from .factory import LLMFactory
from .orchestrator import Orchestrator, LocalInferenceQueue

# Load environment variables from .env if it exists
load_dotenv()

# Global Orchestrator instance
# N=2 for M5 24GB Unified Memory
ORCHESTRATOR = Orchestrator(LocalInferenceQueue(max_concurrent=2))

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    🌌 Event Horizon Core: Unified Local LLM CLI 🌌

    A high-performance orchestration bridge tailored for Apple Silicon (M-Series).
    This CLI manages Metal VRAM, handles request queueing, and routes inference
    through a fallback hierarchy: MLX -> Llama.cpp -> OpenRouter.

    USAGE EXAMPLES:
      Status check:   uv run event-horizon status
      Generate text:  uv run event-horizon generate mlx "What is the event horizon?"
      List MLX models: uv run event-horizon mlx
      List Llama.cpp: uv run event-horizon llamacpp

    Use 'uv run event-horizon help' to see this message again.
    """
    logging.basicConfig(level=logging.INFO) # Switched to INFO to see queue logs
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@main.command()
@click.pass_context
def help(ctx):
    """
    Show this highly detailed help message and exit.
    """
    click.echo(ctx.parent.get_help())

@main.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text", help="Output format.")
@click.option("--verbose", is_flag=True, help="Include hardware and version details.")
def status(format, verbose):
    """
    Check the status of all local LLM providers and list available models.
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
@click.option("--model", help="Specific model ID")
@click.option("--max-tokens", default=500, type=int, help="Maximum number of tokens.")
@click.option("--temp", default=0.7, type=float, help="Temperature.")
@click.option("--json", "json_format", is_flag=True, help="Force output in raw JSON format.")
def generate(provider, prompt, system, model, max_tokens, temp, json_format):
    """
    Generate text using the Orchestrated Inference Bridge.
    """
    async def _run():
        try:
            kwargs = {"max_tokens": max_tokens, "temperature": temp}
            if model:
                if provider == "mlx":
                    kwargs["model_path"] = model
                else:
                    kwargs["model"] = model
            
            # Primary Engine
            engine = LLMFactory.get_provider(provider, **kwargs)
            
            # Setup Fallback if it's a local call
            fallback = None
            if provider in ["mlx", "llamacpp"] and os.environ.get("OPENROUTER_API_KEY"):
                fallback = LLMFactory.get_provider("openrouter")
            elif provider == "mlx":
                # Fallback to local llama.cpp on port 8081
                fallback = LLMFactory.get_provider("llamacpp", base_url="http://127.0.0.1:8081")
            
            if not json_format:
                click.echo(f"\x1b[34m[*] Orchestrating {provider}...\x1b[0m")
            
            # Execute via Orchestrator
            response = await ORCHESTRATOR.generate_with_fallback(
                engine, 
                prompt, 
                system_prompt=system,
                fallback_provider=fallback
            )
            
            if json_format:
                from dataclasses import asdict
                click.echo(json.dumps({
                    "provider": provider, 
                    "model": response.model,
                    "response": response.text,
                    "usage": asdict(response.usage)
                }, indent=2))
            else:
                click.echo("\n\x1b[1m--- Response ---\x1b[0m")
                click.echo(response.text)
                
                # Performance Footer
                usage = response.usage
                if usage.total_tokens > 0:
                    click.echo(f"\n\x1b[2m[Tokens: {usage.total_tokens} | Speed: {usage.tokens_per_second:.2f} tok/s | Latency: {usage.generation_time:.2f}s]\x1b[0m")
        except Exception as e:
            click.echo(f"\x1b[31mError:\x1b[0m {e}", err=True)
            sys.exit(1)

    import os
    asyncio.run(_run())

def _list_provider_models(provider_name, **kwargs):
    """Helper to list models for a specific provider."""
    provider = LLMFactory.get_provider(provider_name, **kwargs)
    click.echo(f"\x1b[1m--- {provider_name.upper()} Models ---\x1b[0m")
    if provider.is_healthy():
        models = provider.list_models()
        if not models:
            click.echo("  (No models found)")
        for m in models:
            click.echo(f"  - {m}")
    else:
        click.echo(f"\x1b[31m[!] {provider_name.upper()} is offline or unreachable.\x1b[0m")

@main.command()
def mlx():
    """List locally available MLX models."""
    _list_provider_models("mlx")

@main.command()
def llamacpp():
    """List available models loaded in the native llama-server."""
    _list_provider_models("llamacpp", base_url="http://127.0.0.1:8081")

@main.command()
def ollama():
    """List locally available Ollama models."""
    _list_provider_models("ollama")

@main.command()
def openrouter():
    """List available OpenRouter models."""
    _list_provider_models("openrouter")

if __name__ == "__main__":
    main()
