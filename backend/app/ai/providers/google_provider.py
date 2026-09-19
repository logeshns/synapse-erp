from google import genai
from google.genai import types

from app.core.config import settings
from app.exceptions import AIProviderException, AITimeoutException


class GoogleAIProvider:
    """Google Gemini API provider implementation using the official google-genai SDK."""

    def complete(self, system_prompt: str, user_prompt: str, timeout_seconds: float = 20.0) -> str:
        if not settings.AI_API_KEY:
            raise AIProviderException("Google AI API key is missing. Please set AI_API_KEY in your .env file.")

        try:
            client = genai.Client(api_key=settings.AI_API_KEY)
            
            # Use gemini-2.5-flash or clean model string
            model_name = settings.AI_MODEL or "gemini-1.5-flash"
            if model_name.startswith("models/"):
                model_name = model_name.replace("models/", "")

            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                ),
            )
            
            output_text = getattr(response, "text", None)
            if not output_text and response.candidates:
                output_text = response.candidates[0].content.parts[0].text

            if not output_text:
                raise AIProviderException("Received empty response from Google AI.")

            cleaned_text = output_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            return cleaned_text.strip()

        except Exception as exc:
            err_msg = str(exc).lower()
            if "timeout" in err_msg or "deadline" in err_msg:
                raise AITimeoutException(f"Google AI request timed out: {exc}")
            raise AIProviderException(f"Google AI provider error: {exc}")