import requests

from app.core.config import settings
from app.exceptions import AIProviderException, AITimeoutException

class OllamaProvider:
    def complete(self, system_prompt: str, user_prompt: str, timeout_seconds: float = 20.0) -> str:
        try:
            response = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.AI_MODEL,
                    "system": system_prompt,
                    "prompt": user_prompt,
                    "stream": False,
                    "format": "json",  # Ollama forces valid JSON output for compatible models
                },
                timeout=timeout_seconds,
            )
            response.raise_for_status()
        except requests.Timeout:
            raise AITimeoutException(f"Ollama did not respond within {timeout_seconds}s.")
        except requests.RequestException as exc:
            raise AIProviderException(f"Could not reach Ollama at {settings.OLLAMA_BASE_URL}: {exc}")

        return response.json().get("response", "")