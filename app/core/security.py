import hashlib
import secrets
from datetime import timedelta

from authx import AuthX, AuthXConfig
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.core.config import settings


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=[
        "bcrypt",
        "argon2",
        "pbkdf2_sha256",
    ],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a new password.

    New passwords use bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a password safely.

    Returns False instead of crashing when the database
    contains an unsupported/invalid password hash.
    """

    if not password_hash:
        return False

    try:
        return pwd_context.verify(
            password,
            password_hash,
        )

    except UnknownHashError:
        return False

    except ValueError:
        return False


# ============================================================
# TOKEN HASHING
# ============================================================

def hash_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ============================================================
# OTP
# ============================================================

def generate_otp(
    length: int = 6,
) -> str:

    if length < 4:
        raise ValueError(
            "OTP length must be at least 4."
        )

    return "".join(
        secrets.choice("0123456789")
        for _ in range(length)
    )


# ============================================================
# AUTHX
# ============================================================

config = AuthXConfig(
    JWT_SECRET_KEY=settings.JWT_SECRET_KEY,

    JWT_TOKEN_LOCATION=[
        "headers",
    ],

    JWT_ACCESS_TOKEN_EXPIRES=timedelta(
        seconds=settings.JWT_ACCESS_TOKEN_EXPIRES_SECONDS
    ),
)


security = AuthX(
    config=config,
)