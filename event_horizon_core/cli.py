import click
import json
import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables (mostly for PATH/API keys)
load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    🌌 Event Horizon Core: M5-Optimized Go Substrate 🌌
    
    This CLI is now a high-performance thin-client proxying inference 
    to the background Go Daemon on Port 8000.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@main.command()
@click.pass_context
def help(ctx):
    """Show this help message."""
    click.echo(ctx.parent.get_help())

@main.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def status(format):
    """Check daemon status and loaded models."""
    try:
        resp = requests.get(f"{BASE_URL}/status")
        resp.raise_for_status()
        data = resp.json()
        
        if format == "json":
            click.echo(json.dumps(data, indent=2))
            return

        click.echo("\x1b[1m--- Event Horizon Daemon Status ---\x1b[0m")
        click.echo(f"[*] Engine: {data.get('engine', 'unknown')}")
        click.echo(f"[*] Port: {data.get('port', 8000)}")
        
        status_raw = data.get("status", "offline")
        color = "\x1b[32m" if status_raw == "running" else "\x1b[31m"
        click.echo(f"[*] Supervisor: {color}{status_raw}\x1b[0m")
        
        if data.get("openrouter"):
            click.echo("[*] Remote (OpenRouter): \x1b[32mEnabled\x1b[0m")
        else:
            click.echo("[*] Remote (OpenRouter): \x1b[33mNot set\x1b[0m")
            
    except Exception as e:
        click.echo(f"\x1b[31m[!] Error: Could not connect to daemon on {BASE_URL}.\x1b[0m", err=True)
        sys.exit(1)

@main.command()
@click.argument("prompt")
@click.option("--model", default="default", help="Specific model hash or alias (best, fast, free)")
@click.option("--max-tokens", default=500, type=int)
@click.option("--temp", default=0.7, type=float)
@click.option("--json", "json_format", is_flag=True, help="Force JSON output.")
def generate(prompt, model, max_tokens, temp, json_format):
    """Perform orchestrated inference (Tier 1: MLX, Tier 3: OpenRouter)."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temp
    }
    
    try:
        if not json_format:
            click.echo(f"\x1b[34m[*] Proxying to Daemon: {model}...\x1b[0m")
            
        resp = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=600)
        resp.raise_for_status()
        data = resp.json()
        
        if json_format:
            click.echo(json.dumps(data, indent=2))
        else:
            click.echo("\n\x1b[1m--- Response ---\x1b[0m")
            click.echo(data["choices"][0]["message"]["content"])
            
            # Print usage if available
            usage = data.get("usage", {})
            if usage:
                click.echo(f"\n\x1b[2m[Tokens: {usage.get('total_tokens', 0)}]\x1b[0m")
                
    except Exception as e:
        click.echo(f"\x1b[31m[!] Request Failed:\x1b[0m {e}", err=True)
        sys.exit(1)

@main.command()
def mlx():
    """Proxy to daemon to list models."""
    status(format="text")

if __name__ == "__main__":
    main()
