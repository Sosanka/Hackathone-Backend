from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # ==========================================
    # APPLICATION
    # ==========================================

    APP_NAME: str = "AgriChoice API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ==========================================
    # DATABASE
    # ==========================================

    DATABASE_URL: str

    # ==========================================
    # CLOUDINARY
    # ==========================================

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # ==========================================
    # SECURITY
    # ==========================================

    SECRET_KEY: str
    JWT_SECRET_KEY: str

    # ==========================================
    # JWT
    # ==========================================

    # 30 days in seconds
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS: int = 60 * 60 * 24 * 30

    # ==========================================
    # SELLER OTP
    # ==========================================

    SELLER_OTP_EXPIRE_MINUTES: int = 10
    SELLER_OTP_MAX_ATTEMPTS: int = 5
    SELLER_OTP_RESEND_COOLDOWN_SECONDS: int = 60

    # ==========================================
    # MAIL
    # ==========================================

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str

    MAIL_FROM_NAME: str = "AgriChoice"

    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"


    BUYER_OTP_EXPIRE_MINUTES: int = 10
    BUYER_OTP_MAX_ATTEMPTS: int = 5
    BUYER_OTP_RESEND_COOLDOWN_SECONDS: int = 60
    # ==========================================
    # PYDANTIC SETTINGS
    # ==========================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()