from app.ai.providers.google_provider import GoogleAIProvider

AIProvider = GoogleAIProvider

def get_ai_provider() -> AIProvider:
    # Hardcoded override to permanently use Google Gemini
    return GoogleAIProvider()