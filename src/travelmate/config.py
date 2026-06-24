from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "TravelMate"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./travelmate.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # 1 hour (was 7 days)
    cors_origins: str = "http://localhost:5173,http://localhost:3000"


settings = Settings()
