from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Hackathone API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str

    SECRET_KEY: str
    JWT_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()