from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Synapse ERP"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+psycopg://synapse:synapse@localhost:5432/synapse_erp"

    JWT_SECRET: str = "change-me-in-env"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    AI_PROVIDER: str = "google"  # "google" | "ollama" | "hosted"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-1.5-flash"
    AI_BASE_URL: str = ""  
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    FRONTEND_URL: str = "http://localhost:5173"


settings = Settings()