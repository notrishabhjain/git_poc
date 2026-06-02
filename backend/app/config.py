from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://assistant:changeme@localhost:5432/assistant"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Encryption
    encryption_secret: str = "changeme"

    # AI Providers
    groq_api_key: str = ""
    nvidia_api_key: str = ""
    cerebras_api_key: str = ""

    # Google Calendar
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # ntfy.sh
    ntfy_topic: str = "whatsapp-assistant"
    ntfy_token: str = ""

    # Auth
    jwt_secret: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24h
    dashboard_password: str = "changeme"

    # Bridge
    bridge_shared_secret: str = "changeme"
    bridge_url: str = "http://localhost:3001"
    backend_webhook_url: str = "http://localhost:8000/api/v1/webhooks/whatsapp/message"

    # App
    timezone: str = "Asia/Kolkata"
    working_hours_start: str = "09:00"
    working_hours_end: str = "19:00"

    # AI model preferences
    classifier_model: str = "llama-3.1-8b-instant"   # Groq
    extractor_model: str = "meta/llama-3.3-70b-instruct"  # NVIDIA Build
    whisper_model: str = "whisper-large-v3-turbo"    # Groq


settings = Settings()
