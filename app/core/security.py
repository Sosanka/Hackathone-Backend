from authx import AuthX, AuthXConfig

from app.core.config import settings


config = AuthXConfig()

config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
config.JWT_TOKEN_LOCATION = ["headers"]


security = AuthX(config=config)