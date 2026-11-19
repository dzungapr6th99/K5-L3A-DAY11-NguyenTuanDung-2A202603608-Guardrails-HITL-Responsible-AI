"""Check Jetson connectivity, installed models and the actual lab runtime."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.config import get_blue_provider, get_red_provider, ollama_client_kwargs
from core.openai_runtime import create_blue_pair, create_openai_pair


async def main(advance: bool) -> None:
    base = ollama_client_kwargs()["base_url"].removesuffix("/v1")
    with urlopen(base + "/api/version", timeout=10) as response:
        print("Ollama:", json.load(response)["version"], "at", base)
    with urlopen(base + "/api/tags", timeout=10) as response:
        print("Models:", ", ".join(m["name"] for m in json.load(response)["models"]))
    for label, provider, factory in (
        ("Blue", get_blue_provider(), create_blue_pair),
        ("Red", get_red_provider(), create_openai_pair),
    ):
        if provider != "ollama":
            print(f"{label}: skipped (configured provider={provider})")
            continue
        agent, runner = factory(
            name="connectivity_check", app_name="connectivity_check",
            instruction="Reply briefly to ordinary banking questions.",
        )
        answer = await runner.chat(agent, "What is a savings account? Answer in one sentence.")
        print(f"{label} [{runner.provider}:{runner.model}]: {answer}")
    if advance:
        from agents.guards_agent import create_red_agent_advance

        agent, runner = create_red_agent_advance()
        answer = await runner.chat(agent, "What is a savings account?")
        print("Red Advance:", answer)
        plugin = runner.plugins[0]
        print("NeMo stats:", plugin.nemo.stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--advance", action="store_true", help="Also check Red Advance and NeMo")
    args = parser.parse_args()
    try:
        asyncio.run(main(args.advance))
    except Exception as exc:
        print(f"Check failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
