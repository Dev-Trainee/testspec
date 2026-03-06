"""LLM integration — supports OpenAI-compatible APIs."""

from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI
from rich.console import Console

console = Console()


class LLMClient:
    """Thin wrapper around OpenAI-compatible chat completions."""

    def __init__(
        self,
        model: str = "gpt-4o",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_key_env: str = "OPENAI_API_KEY",
        temperature: float = 0.3,
    ):
        self.model = model
        self.temperature = temperature

        resolved_key = api_key or os.environ.get(api_key_env, "")
        if not resolved_key:
            console.print(
                f"[yellow]Warning: No API key found. Set {api_key_env} or pass --api-key.[/yellow]"
            )

        kwargs: dict = {"api_key": resolved_key or "sk-placeholder"}
        if base_url:
            kwargs["base_url"] = base_url

        self._client = OpenAI(**kwargs)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send a chat completion request and return the assistant message."""
        console.print("[dim]Calling LLM...[/dim]")
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = resp.choices[0].message.content or ""
            return content.strip()
        except Exception as exc:
            console.print(f"[red]LLM call failed: {exc}[/red]")
            raise
