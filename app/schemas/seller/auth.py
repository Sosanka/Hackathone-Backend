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

class SellerRegisterRequest(BaseModel):

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
                "Seller name cannot be empty."
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

class SellerRegisterResponse(BaseModel):

    message: str

    email: EmailStr


# ==================================================
# VERIFY OTP
# ==================================================

class SellerVerifyOTPRequest(BaseModel):

    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class SellerVerifyOTPResponse(BaseModel):

    message: str


# ==================================================
# RESEND OTP
# ==================================================

class SellerResendOTPRequest(BaseModel):

    email: EmailStr


# ==================================================
# LOGIN
# ==================================================

class SellerLoginRequest(BaseModel):

    email: EmailStr

    password: str


class SellerLoginResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    expires_at: datetime


# ==================================================
# ME
# ==================================================

class SellerMeResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    name: str

    email: EmailStr

    phone: str

    is_email_verified: bool

    is_active: bool