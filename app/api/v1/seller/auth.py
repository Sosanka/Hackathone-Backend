from datetime import (
    datetime,
    timedelta,
    timezone,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

from app.core.mailer import (
    send_seller_otp_email,
)

from app.core.security import (
    hash_password,
    hash_token,
    security,
    verify_password,
)

from app.models.seller.seller import Seller

from app.models.seller.seller_otp import (
    SellerEmailOTP,
)

from app.models.seller.seller_session import (
    SellerSession,
)

from app.schemas.seller.auth import (
    SellerLoginRequest,
    SellerLoginResponse,
    SellerMeResponse,
    SellerRegisterRequest,
    SellerRegisterResponse,
    SellerResendOTPRequest,
    SellerVerifyOTPRequest,
    SellerVerifyOTPResponse,
)

from app.services.seller.auth import (
    get_current_seller,
)

from app.services.seller.otp import (
    create_seller_otp,
)


router = APIRouter(
    prefix="/seller/auth",
    tags=[
        "Seller Authentication"
    ],
)


# ==================================================
# REGISTER
# ==================================================

@router.post(
    "/register",
    response_model=SellerRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_seller(

    data: SellerRegisterRequest,

    db: AsyncSession = Depends(
        get_db
    ),

):

    email = (
        data.email
        .lower()
        .strip()
    )

    phone = data.phone.strip()

    name = data.name.strip()

    # ==========================================
    # Check email
    # ==========================================

    result = await db.execute(

        select(Seller)

        .where(
            Seller.email == email
        )

    )

    existing_seller = (
        result.scalar_one_or_none()
    )

    if existing_seller:

        # --------------------------------------
        # Already verified
        # --------------------------------------

        if existing_seller.is_email_verified:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,

                detail={
                    "code": "EMAIL_EXISTS",
                    "field": "email",
                    "message": (
                        "An account with this "
                        "email already exists."
                    ),
                },
            )

        # --------------------------------------
        # Existing unverified account
        # --------------------------------------

        existing_seller.name = name

        existing_seller.phone = phone

        existing_seller.password_hash = (
            hash_password(
                data.password
            )
        )

        try:

            otp = await create_seller_otp(
                db,
                existing_seller.id,
            )

            await db.commit()

            await send_seller_otp_email(
                email=existing_seller.email,
                seller_name=existing_seller.name,
                otp=otp,
            )

        except HTTPException:

            await db.rollback()

            raise

        except Exception:

            await db.rollback()

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Unable to send verification "
                    "email. Please try again."
                ),
            )

        return SellerRegisterResponse(
            message=(
                "Verification OTP sent "
                "to your email."
            ),
            email=email,
        )

    # ==========================================
    # Check phone
    # ==========================================

    result = await db.execute(

        select(Seller)

        .where(
            Seller.phone == phone
        )

    )

    existing_phone = (
        result.scalar_one_or_none()
    )

    if existing_phone:

        raise HTTPException(

            status_code=status.HTTP_409_CONFLICT,

            detail={
                "code": "PHONE_EXISTS",
                "field": "phone",
                "message": (
                    "An account with this "
                    "phone number already exists."
                ),
            },
        )

    # ==========================================
    # Create seller
    # ==========================================

    seller = Seller(

        name=name,

        email=email,

        phone=phone,

        password_hash=hash_password(
            data.password
        ),

        is_email_verified=False,

        is_active=True,
    )

    db.add(seller)

    await db.flush()

    # ==========================================
    # Create OTP
    # ==========================================

    otp = await create_seller_otp(
        db,
        seller.id,
    )

    # ==========================================
    # Commit seller + OTP
    # ==========================================

    await db.commit()

    # ==========================================
    # Send email
    # ==========================================

    try:

        await send_seller_otp_email(

            email=seller.email,

            seller_name=seller.name,

            otp=otp,

        )

    except Exception:

        raise HTTPException(

            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),

            detail=(
                "Account created successfully, "
                "but the verification email could "
                "not be sent. Please request a new OTP."
            ),
        )

    return SellerRegisterResponse(

        message=(
            "Account created successfully. "
            "Verification OTP sent to your email."
        ),

        email=seller.email,

    )


# ==================================================
# VERIFY OTP
# ==================================================

@router.post(
    "/verify-otp",
    response_model=SellerVerifyOTPResponse,
)
async def verify_seller_otp(

    data: SellerVerifyOTPRequest,

    db: AsyncSession = Depends(
        get_db
    ),

):

    email = (
        data.email
        .lower()
        .strip()
    )

    # ==========================================
    # Find seller
    # ==========================================

    result = await db.execute(

        select(Seller)

        .where(
            Seller.email == email
        )

    )

    seller = (
        result.scalar_one_or_none()
    )

    if seller is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail={
                "code": "SELLER_NOT_FOUND",
                "field": "email",
                "message": (
                    "Seller account not found."
                ),
            },
        )

    if seller.is_email_verified:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail={
                "code": "EMAIL_ALREADY_VERIFIED",
                "message": (
                    "Email is already verified."
                ),
            },
        )

    # ==========================================
    # Latest OTP
    # ==========================================

    result = await db.execute(

        select(SellerEmailOTP)

        .where(

            SellerEmailOTP.seller_id
            == seller.id,

            SellerEmailOTP.is_used.is_(False),

        )

        .order_by(
            SellerEmailOTP.created_at.desc()
        )

        .limit(1)

    )

    otp_record = (
        result.scalar_one_or_none()
    )

    if otp_record is None:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail={
                "code": "OTP_NOT_FOUND",
                "message": (
                    "Verification OTP not found. "
                    "Please request a new OTP."
                ),
            },
        )

    # ==========================================
    # Expiration
    # ==========================================

    now = datetime.now(
        timezone.utc
    )

    if otp_record.expires_at <= now:

        otp_record.is_used = True

        await db.commit()

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail={
                "code": "OTP_EXPIRED",
                "message": (
                    "OTP has expired. "
                    "Please request a new OTP."
                ),
            },
        )

    # ==========================================
    # Attempt limit
    # ==========================================

    if (
        otp_record.attempts
        >= settings.SELLER_OTP_MAX_ATTEMPTS
    ):

        otp_record.is_used = True

        await db.commit()

        raise HTTPException(

            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),

            detail={
                "code": "OTP_ATTEMPTS_EXCEEDED",
                "message": (
                    "Too many incorrect attempts. "
                    "Please request a new OTP."
                ),
            },
        )

    # ==========================================
    # Verify OTP
    # ==========================================

    provided_hash = hash_token(
        data.otp
    )

    if provided_hash != otp_record.otp_hash:

        otp_record.attempts += 1

        await db.commit()

        remaining = (
            settings.SELLER_OTP_MAX_ATTEMPTS
            - otp_record.attempts
        )

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail={
                "code": "INVALID_OTP",
                "message": (
                    "Invalid OTP."
                ),
                "attempts_remaining": remaining,
            },
        )

    # ==========================================
    # Verify account
    # ==========================================

    seller.is_email_verified = True

    otp_record.is_used = True

    # ==========================================
    # Create 30-day authentication expiration
    # ==========================================

    now = datetime.now(
        timezone.utc
    )

    expires_at = (
        now
        + timedelta(
            seconds=settings.JWT_ACCESS_TOKEN_EXPIRES
        )
    )

    # ==========================================
    # Create JWT
    # ==========================================

    token = security.create_access_token(

        uid=str(
            seller.id
        ),

        data={
            "role": "seller",
            "seller_id": seller.id,
        },

    )

    # ==========================================
    # Store session in database
    # ==========================================

    session = SellerSession(

        seller_id=seller.id,

        token_hash=hash_token(
            token
        ),

        expires_at=expires_at,

        is_active=True,

    )

    db.add(session)

    # ==========================================
    # Commit:
    # Seller verification
    # OTP usage
    # Session creation
    # ==========================================

    await db.commit()

    # ==========================================
    # Return authenticated session
    # ==========================================

    return SellerVerifyOTPResponse(

        message=(
            "Email verified successfully. "
            "Your seller account is now active."
        ),

        access_token=token,

        token_type="bearer",

        expires_at=expires_at,

    )


# ==================================================
# RESEND OTP
# ==================================================

@router.post(
    "/resend-otp",
    response_model=SellerRegisterResponse,
)
async def resend_seller_otp(

    data: SellerResendOTPRequest,

    db: AsyncSession = Depends(
        get_db
    ),

):

    email = (
        data.email
        .lower()
        .strip()
    )

    # ==========================================
    # Find seller
    # ==========================================

    result = await db.execute(

        select(Seller)

        .where(
            Seller.email == email
        )

    )

    seller = (
        result.scalar_one_or_none()
    )

    if seller is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail={
                "code": "SELLER_NOT_FOUND",
                "message": (
                    "Seller account not found."
                ),
            },
        )

    if seller.is_email_verified:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail={
                "code": "EMAIL_ALREADY_VERIFIED",
                "message": (
                    "Email is already verified."
                ),
            },
        )

    # ==========================================
    # Generate OTP
    # ==========================================

    otp = await create_seller_otp(

        db,

        seller.id,

    )

    await db.commit()

    # ==========================================
    # Send
    # ==========================================

    try:

        await send_seller_otp_email(

            email=seller.email,

            seller_name=seller.name,

            otp=otp,

        )

    except Exception:

        raise HTTPException(

            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),

            detail=(
                "Unable to send OTP. "
                "Please try again later."
            ),

        )

    return SellerRegisterResponse(

        message=(
            "A new verification OTP "
            "has been sent."
        ),

        email=seller.email,

    )


# ==================================================
# LOGIN
# ==================================================

@router.post(
    "/login",
    response_model=SellerLoginResponse,
)
async def seller_login(

    data: SellerLoginRequest,

    db: AsyncSession = Depends(
        get_db
    ),

):

    email = (
        data.email
        .lower()
        .strip()
    )

    # ==========================================
    # Find seller
    # ==========================================

    result = await db.execute(

        select(Seller)

        .where(
            Seller.email == email
        )

    )

    seller = (
        result.scalar_one_or_none()
    )

    # ==========================================
    # Generic credential error
    # ==========================================

    if seller is None:

        raise HTTPException(

            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),

            detail={
                "code": "INVALID_CREDENTIALS",
                "message": (
                    "Invalid email or password."
                ),
            },
        )

    # ==========================================
    # Password
    # ==========================================

    if not verify_password(

        data.password,

        seller.password_hash,

    ):

        raise HTTPException(

            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),

            detail={
                "code": "INVALID_CREDENTIALS",
                "message": (
                    "Invalid email or password."
                ),
            },
        )

    # ==========================================
    # Email verification
    # ==========================================

    if not seller.is_email_verified:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail={
                "code": "EMAIL_NOT_VERIFIED",
                "message": (
                    "Please verify your email "
                    "before logging in."
                ),
            },
        )

    # ==========================================
    # Account status
    # ==========================================

    if not seller.is_active:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail={
                "code": "ACCOUNT_INACTIVE",
                "message": (
                    "Seller account is inactive."
                ),
            },
        )

    # ==========================================
    # Expiration
    # ==========================================

    now = datetime.now(
        timezone.utc
    )

    expires_at = (

        now

        + timedelta(
            seconds=(
                settings.JWT_ACCESS_TOKEN_EXPIRES
            )
        )

    )

    # ==========================================
    # Create JWT
    # ==========================================

    token = security.create_access_token(

        uid=str(
            seller.id
        ),

        data={
            "role": "seller",
            "seller_id": seller.id,
        },

    )

    # ==========================================
    # Database session
    # ==========================================

    session = SellerSession(

        seller_id=seller.id,

        token_hash=hash_token(
            token
        ),

        expires_at=expires_at,

        is_active=True,

    )

    db.add(session)

    await db.commit()

    return SellerLoginResponse(

        access_token=token,

        token_type="bearer",

        expires_at=expires_at,

    )


# ==================================================
# CURRENT SELLER
# ==================================================

@router.get(
    "/me",
    response_model=SellerMeResponse,
)
async def seller_me(

    seller: Seller = Depends(
        get_current_seller
    ),

):

    return seller


# ==================================================
# LOGOUT
# ==================================================

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def seller_logout(

    request: Request,

    seller: Seller = Depends(
        get_current_seller
    ),

    db: AsyncSession = Depends(
        get_db
    ),

):

    authorization = request.headers.get(
        "Authorization"
    )

    if not authorization:

        raise HTTPException(

            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),

            detail="Authentication token missing.",

        )

    scheme, _, token = (
        authorization.partition(" ")
    )

    if (

        scheme.lower() != "bearer"

        or not token

    ):

        raise HTTPException(

            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),

            detail="Invalid authorization header.",

        )

    token_hash = hash_token(
        token
    )

    # ==========================================
    # Find current session
    # ==========================================

    result = await db.execute(

        select(SellerSession)

        .where(

            SellerSession.token_hash
            == token_hash,

            SellerSession.seller_id
            == seller.id,

        )

    )

    session = (
        result.scalar_one_or_none()
    )

    if session:

        session.is_active = False

        await db.commit()

    return None