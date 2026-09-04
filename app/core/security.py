import hashlib
import secrets

from authx import AuthX, AuthXConfig
from pwdlib import PasswordHash

from app.core.config import settings


# ==================================================
# PASSWORD HASHING
# ==================================================

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash password using Argon2.
    """
    return password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify password against Argon2 hash.
    """
    return password_hasher.verify(
        password,
        password_hash,
    )


# ==================================================
# AUTHX
# ==================================================

config = AuthXConfig(
    JWT_SECRET_KEY=settings.JWT_SECRET_KEY,

    JWT_TOKEN_LOCATION=[
        "headers"
    ],

    JWT_ALGORITHM="HS256",

    JWT_ACCESS_TOKEN_EXPIRES=(
        settings.JWT_ACCESS_TOKEN_EXPIRES
    ),
)


security = AuthX(
    config=config
)


# ==================================================
# TOKEN HASH
# ==================================================

def hash_token(token: str) -> str:
    """
    SHA-256 hash for storing JWT/session
    identifiers safely in database.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ==================================================
# OTP
# ==================================================

def generate_otp() -> str:
    """
    Generate cryptographically secure 6 digit OTP.
    """

    return f"{secrets.randbelow(1_000_000):06d}"