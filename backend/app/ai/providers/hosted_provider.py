import requests

from app.core.config import settings
from app.exceptions import AIProviderException, AITimeoutException


class HostedProvider:
    """Generic OpenAI-compatible chat-completions client — works against
    any provider that implements that interface. The specific provider,
    AI_BASE_URL and auth header get confirmed at Phase 16 deployment once
    current free-tier terms are verified; left generic until then."""

    def complete(self, system_prompt: str, user_prompt: str, timeout_seconds: float = 20.0) -> str:
        if not settings.AI_BASE_URL or not settings.AI_API_KEY:
            raise AIProviderException("Hosted AI provider is not configured (AI_BASE_URL/AI_API_KEY missing).")

        try:
            response = requests.post(
                f"{settings.AI_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {settings.AI_API_KEY}"},
                json={
                    "model": settings.AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
                timeout=timeout_seconds,
            )
            response.raise_for_status()
        except requests.Timeout:
            raise AITimeoutException(f"Hosted AI provider did not respond within {timeout_seconds}s.")
        except requests.RequestException as exc:
            raise AIProviderException(f"Hosted AI provider request failed: {exc}")

        return response.json()["choices"][0]["message"]["content"]