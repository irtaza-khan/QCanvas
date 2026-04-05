"""
Quick smoke test for the configured Ollama model.

Usage:
    python scripts/test_ollama_model.py \
        --model qwen2.5-coder:14b-instruct-q4_K_M \
        --prompt "Write a minimal Cirq Bell state example."

The script:
    1. Pings the Ollama server to verify it is reachable.
    2. Sends a single chat request with the given prompt.
    3. Measures latency and reports simple output statistics.
"""

from __future__ import annotations

import argparse
import os
import time
from typing import Any, Dict

import requests


def ping_ollama(base_url: str) -> Dict[str, Any]:
    """Fetch the list of available models to ensure the server is up."""
    resp = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=5)
    resp.raise_for_status()
    return resp.json()


def run_chat(
    base_url: str,
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
) -> Dict[str, Any]:
    """Send a single chat completion request to Ollama."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert Google Cirq quantum computing programmer."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }
    resp = requests.post(f"{base_url.rstrip('/')}/api/chat", json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Test a local Ollama model.")
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:14b-instruct-q4_K_M",
        help="Ollama model tag to test.",
    )
    parser.add_argument(
        "--prompt",
        default="Write a minimal Cirq circuit that prepares and measures a Bell state.",
        help="Prompt to send to the model.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Temperature to use for generation.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=800,
        help="Maximum tokens (num_predict) for the response.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        help="Base URL of the Ollama server.",
    )
    args = parser.parse_args()

    print(f"🔌 Ollama base URL: {args.base_url}")
    print("📡 Pinging Ollama server...")
    ping_start = time.perf_counter()
    tags = ping_ollama(args.base_url)
    ping_time = time.perf_counter() - ping_start
    available_models = [m.get("name") for m in tags.get("models", [])]
    print(f"✅ Server responded in {ping_time:.2f}s; {len(available_models)} models available.")
    if args.model not in available_models:
        print(
            f"⚠️  Model '{args.model}' not reported by /api/tags. "
            "If you just pulled it, this might still be fine."
        )

    print(f"\n🧠 Testing model '{args.model}' with prompt:\n{args.prompt}\n")
    start = time.perf_counter()
    response = run_chat(
        base_url=args.base_url,
        model=args.model,
        prompt=args.prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    elapsed = time.perf_counter() - start

    message = response.get("message", {})
    content = message.get("content", "").strip()
    eval_info = response.get("eval_info", {})

    print("✅ Response received.")
    print(f"⏱  Total latency: {elapsed:.2f}s")
    if eval_info:
        prompt_tokens = eval_info.get("prompt_eval_count")
        response_tokens = eval_info.get("eval_count")
        if prompt_tokens is not None and response_tokens is not None:
            print(f"🧮 Tokens — prompt: {prompt_tokens}, response: {response_tokens}")

    print(f"\n--- Model Output (first 400 chars) ---\n{content[:2000]}")
    if len(content) > 2000:
        print("... (truncated)")


if __name__ == "__main__":
    main()
