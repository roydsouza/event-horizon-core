import click
import json
import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables (mostly for PATH/API keys)
load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)

@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    🌌 Event Horizon Core: M5-Optimized Go Substrate 🌌
    
    High-performance thin-client proxying inference to the background Go Daemon (Port 8000).

    \b
    🏗️ ARCHITECTURE: LOCAL-ONLY (MLX)
    -------------------------------------------------------
    Tier 1 (Local):  Run free models natively on your M5. 
                     (Built for 24GB VRAM. Stay <15B params).
                     Recs: Hermes-3-Llama-3.1-8B, Llama-3.2-3B.
    
    \b
    🔧 EXPLICIT MODEL CONTROL:
    -------------------------------------------------------
    Provide any valid HuggingFace path that supports MLX.
    
    Examples:
    --model "mlx-community/Hermes-3-Llama-3.1-8B-4bit"
    --model "mlx-community/Llama-3.2-3B-Instruct-4bit"

    \b
    💡 HELP & USAGE
    -------------------------------------------------------
    Run 'event-horizon <command> --help' for detailed option
    lists for specific actions like 'generate' or 'status'.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

def _fetch_status(format="text"):
    """Internal helper to fetch status from daemon."""
    try:
        resp = requests.get(f"{BASE_URL}/status")
        resp.raise_for_status()
        data = resp.json()
        
        if format == "json":
            return json.dumps(data, indent=2)

        lines = [
            "\x1b[1m--- Event Horizon Daemon Status ---\x1b[0m",
            f"[*] Engine:     {data.get('engine', 'unknown')}",
            f"[*] Port:       {data.get('port', 8000)}",
        ]
        
        status_raw = data.get("status", "offline")
        color = "\x1b[32m" if status_raw == "running" else "\x1b[31m"
        lines.append(f"[*] Supervisor: {color}{status_raw}\x1b[0m")
            
        return "\n".join(lines)
            
    except Exception:
        return f"\x1b[31m[!] Error: Could not connect to daemon on {BASE_URL}.\x1b[0m"

@main.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text", help="Output format.")
def status(format):
    """
    Check daemon status and loaded models.
    
    This command queries the background Go daemon (Port 8000) to check 
    if the supervisor is active and if the MLX server is healthy.
    """
    click.echo(_fetch_status(format=format))

@main.command()
@click.argument("prompt")
@click.option("--model", default="default", help="Specific model alias (best, free) or MLX path.")
@click.option("--max-tokens", default=500, type=int, help="Max tokens to generate (Default: 500).")
@click.option("--temp", default=0.7, type=float, help="Sampling temperature (0.0 - 1.0).")
@click.option("--json", "json_format", is_flag=True, help="Return raw OpenAI-compatible JSON response.")
def generate(prompt, model, max_tokens, temp, json_format):
    """
    Perform local inference using MLX.
    
    EXAMPLES:
    \b
    1. Local Inference (HuggingFace path):
       event-horizon generate "Hello" --model "mlx-community/Hermes-3-Llama-3.1-8B-4bit"
    
    2. Optimized Local (Auto-Swapping):
       event-horizon generate "Research PQC" # Uses currently loaded default model
    """
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temp
    }
    
    try:
        if not json_format:
            click.echo(f"\x1b[34m[*] Requesting {model} via Daemon...\x1b[0m")
            
        resp = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=600)
        resp.raise_for_status()
        data = resp.json()
        
        if json_format:
            click.echo(json.dumps(data, indent=2))
        else:
            click.echo("\n\x1b[1m--- Response ---\x1b[0m")
            click.echo(data["choices"][0]["message"]["content"])
            
            usage = data.get("usage", {})
            if usage:
                click.echo(f"\n\x1b[2m[Tokens: {usage.get('total_tokens', 0)}]\x1b[0m")
                
    except Exception as e:
        click.echo(f"\x1b[31m[!] Request Failed:\x1b[0m {e}", err=True)
        sys.exit(1)

@main.command()
def mlx():
    """
    Check the status of the local MLX inference engine.
    
    This is a shorthand alias for 'event-horizon status'. 
    It verifies if the background mlx_lm.server is supervised 
    and healthy on Port 8080.
    
    Tier 1 (Local) depends on this engine being 'running'.
    """
    click.echo(_fetch_status(format="text"))

if __name__ == "__main__":
    main()
