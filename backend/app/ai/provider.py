from typing import Protocol

from app.ai.providers.google_provider import GoogleAIProvider
from app.ai.providers.hosted_provider import HostedProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.core.config import settings


class AIProvider(Protocol):
    def complete(self, system_prompt: str, user_prompt: str, timeout_seconds: float = 20.0) -> str:
        """Return the raw model response text. Callers are responsible for
        parsing/validating it — this layer only knows how to talk to the
        provider, nothing about order schemas."""
        ...


def get_ai_provider() -> AIProvider:
    """FastAPI dependency — swap AI_PROVIDER in .env to change providers
    with zero code changes in agents or services."""
    provider_type = (settings.AI_PROVIDER or "google").lower()
    
    if provider_type in ("google", "gemini"):
        return GoogleAIProvider()
    if provider_type == "hosted":
        return HostedProvider()
        
    return OllamaProvider()