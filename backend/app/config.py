from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Base de Datos
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_secret"
    POSTGRES_DB: str = "mapa_sabores"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres_secret@localhost:5432/mapa_sabores"
    )

    # Seguridad & Autenticación
    JWT_SECRET_KEY: str = "super_secret_jwt_key_min_32_chars_default"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # Servicios de IA Externa
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_PRIMARY_PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"
    LLM_TIMEOUT_SECONDS: float = 8.0

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
