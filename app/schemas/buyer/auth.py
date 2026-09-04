from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


# ==================================================
# REGISTER
# ==================================================

class BuyerRegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    phone: str = Field(
        min_length=10,
        max_length=20,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError(
                "Buyer name cannot be empty."
            )

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError(
                "Phone number cannot be empty."
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):

        if not any(
            char.isupper()
            for char in value
        ):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not any(
            char.islower()
            for char in value
        ):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )

        if not any(
            char.isdigit()
            for char in value
        ):
            raise ValueError(
                "Password must contain at least one number."
            )

        return value


# ==================================================
# REGISTER RESPONSE
# ==================================================

class BuyerRegisterResponse(BaseModel):

    message: str

    email: EmailStr


# ==================================================
# VERIFY OTP
# ==================================================

class BuyerVerifyOTPRequest(BaseModel):

    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class BuyerVerifyOTPResponse(BaseModel):

    message: str

    access_token: str

    token_type: str = "bearer"

    expires_at: datetime


# ==================================================
# RESEND OTP
# ==================================================

class BuyerResendOTPRequest(BaseModel):

    email: EmailStr


# ==================================================
# LOGIN
# ==================================================

class BuyerLoginRequest(BaseModel):

    email: EmailStr

    password: str


class BuyerLoginResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    expires_at: datetime


# ==================================================
# ME
# ==================================================

class BuyerMeResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    name: str

    email: EmailStr

    phone: str

    is_email_verified: bool

    is_active: bool