from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

try:
    import openai
except ImportError:  # pragma: no cover - optional dependency
    openai = None


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: Any,
    ) -> str:
        """Generate a chat completion given message history."""


class OpenAIProvider(LLMProvider):
    def __init__(self, client: Optional[Any] = None):
        if openai is None:
            raise ImportError("openai package is required for OpenAIProvider")
        self.client = client or openai.Client()

    def generate(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: Any,
    ) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return response.choices[0].message.content


class AnthropicProvider(LLMProvider):
    """Placeholder for a future Anthropic integration."""

    def generate(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError("AnthropicProvider is not implemented yet")


class DummyProvider(LLMProvider):
    """A deterministic provider useful for tests and offline development."""

    def __init__(self, template: str = "{persona}: {content}"):
        self.template = template

    def generate(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: Any,
    ) -> str:
        # Use the last user message for simplicity
        user_messages = [m for m in messages if m["role"] == "user"]
        persona = kwargs.get("persona_id", "anonymous")
        content = user_messages[-1]["content"] if user_messages else ""
        return self.template.format(persona=persona, content=content)
