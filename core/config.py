import json
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST:     str = "localhost"
    DB_PORT:     int = 3306
    DB_USER:     str = "root"
    DB_PASSWORD: str = ""
    DB_NAME:     str = "fluvialert"

    # JWT Settings
    SECRET_KEY:  str = "development_secret_key_change_me_in_production"
    ALGORITHM:   str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # CORS — aceita string JSON ou lista via env
    CORS_ORIGINS: str = '["http://localhost:5173","http://127.0.0.1:5173"]'

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origins_list(self) -> list[str]:
        """Converte a string JSON de origens CORS em uma lista."""
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return [self.CORS_ORIGINS]


settings = Settings()
