from pydantic_settings import BaseSettings


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

    class Config:
        env_file = ".env"


settings = Settings()
