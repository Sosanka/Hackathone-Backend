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
    send_buyer_otp_email,
)

from app.core.security import (
    hash_password,
    hash_token,
    security,
    verify_password,
)

from app.models.buyer.buyer import Buyer

from app.models.buyer.buyer_otp import (
    BuyerEmailOTP,
)

from app.models.buyer.buyer_session import (
    BuyerSession,
)

from app.schemas.buyer.auth import (
    BuyerLoginRequest,
    BuyerLoginResponse,
    BuyerMeResponse,
    BuyerRegisterRequest,
    BuyerRegisterResponse,
    BuyerResendOTPRequest,
    BuyerVerifyOTPRequest,
    BuyerVerifyOTPResponse,
)

from app.services.buyer.auth import (
    get_current_buyer,
)

from app.services.buyer.otp import (
    create_buyer_otp,
)


router = APIRouter(
    prefix="/buyer/auth",
    tags=[
        "Buyer Authentication"
    ],
)


# ==================================================
# REGISTER
# ==================================================

@router.post(
    "/register",
    response_model=BuyerRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_buyer(

    data: BuyerRegisterRequest,

    db: AsyncSession = Depends(
        get_db
    ),

):

    email = (
        str(data.email)
        .lower()
        .strip()
    )

    phone = data.phone.strip()

    name = data.name.strip()

    # ==========================================
    # Check email
    # ==========================================

    result = await db.execute(

        select(Buyer)

        .where(
            Buyer.email == email
        )

    )

    existing_buyer = (
        result.scalar_one_or_none()
    )

    if existing_buyer:

        # --------------------------------------
        # Already verified
        # --------------------------------------

        if existing_buyer.is_email_verified:

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
        # Check phone owner
        # --------------------------------------

        phone_result = await db.execute(

            select(Buyer)

            .where(

                Buyer.phone == phone,

                Buyer.id != existing_buyer.id,

            )

        )

        if phone_result.scalar_one_or_none():

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

        # --------------------------------------
        # Update unverified buyer
        # --------------------------------------

        existing_buyer.name = name

        existing_buyer.phone = phone

        existing_buyer.password_hash = (
            hash_password(
                data.password
            )
        )

        try:

            otp = await create_buyer_otp(
                db,
                existing_buyer.id,
            )

            await db.commit()

        except HTTPException:

            await db.rollback()

            raise

        try:

            await send_buyer_otp_email(
                email=existing_buyer.email,
                buyer_name=existing_buyer.name,
                otp=otp,
            )

        except Exception:

            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail=(
                    "Unable to send verification "
                    "email. Please try again."
                ),
            )

        return BuyerRegisterResponse(

            message=(
                "Verification OTP sent "
                "to your email."
            ),

            email=existing_buyer.email,

        )

    # ==========================================
    # Check phone
    # ==========================================

    result = await db.execute(

        select(Buyer)

        .where(
            Buyer.phone == phone
        )

    )

    if result.scalar_one_or_none():

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
    # Create buyer
    # ==========================================

    buyer = Buyer(

        name=name,

        email=email,

        phone=phone,

        password_hash=hash_password(
            data.password
        ),

        is_email_verified=False,

        is_active=True,

    )

    db.add(
        buyer
    )

    try:

        await db.flush()

        otp = await create_buyer_otp(
            db,
            buyer.id,
        )

        await db.commit()

    except HTTPException:

        await db.rollback()

        raise

    except Exception:

        await db.rollback()

        raise

    # ==========================================
    # Send OTP
    # ==========================================

    try:

        await send_buyer_otp_email(
            email=buyer.email,
            buyer_name=buyer.name,
            otp=otp,
        )

    except Exception:

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Unable to send verification "
                "email. Please try again."
            ),
        )

    return BuyerRegisterResponse(

        message=(
            "Verification OTP sent "
            "to your email."
        ),

        email=buyer.email,

    )


# ==================================================
# VERIFY OTP
# ==================================================

@router.post(
    "/verify-otp",
    response_model=BuyerVerifyOTPResponse,
)
async def verify_buyer_otp(

    data: BuyerVerifyOTPRequest,

    db: AsyncSession = Depends(
        get_db
    ),

):

    email = (
        str(data.email)
        .lower()
        .strip()
    )

    # ==========================================
    # Find buyer
    # ==========================================

    result = await db.execute(

        select(Buyer)

        .where(
            Buyer.email == email
        )

    )

    buyer = (
        result.scalar_one_or_none()
    )

    if buyer is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "BUYER_NOT_FOUND",
                "message": (
                    "Buyer account not found."
                ),
            },
        )

    if buyer.is_email_verified:

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

        select(BuyerEmailOTP)

        .where(

            BuyerEmailOTP.buyer_id
            == buyer.id,

            BuyerEmailOTP.is_used.is_(False),

        )

        .order_by(
            BuyerEmailOTP.created_at.desc()
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

    otp_expires_at = (
        otp_record.expires_at
    )

    if otp_expires_at.tzinfo is None:

        otp_expires_at = (
            otp_expires_at.replace(
                tzinfo=timezone.utc
            )
        )

    if otp_expires_at <= now:

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
    # Attempts
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

    if (
        provided_hash
        != otp_record.otp_hash
    ):

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
                "message": "Invalid OTP.",
                "attempts_remaining": remaining,
            },
        )

    # ==========================================
    # Verify buyer
    # ==========================================

    buyer.is_email_verified = True

    otp_record.is_used = True

    # ==========================================
    # Session expiration
    # ==========================================

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
        uid=str(buyer.id),
    )

    # ==========================================
    # Store session
    # ==========================================

    session = BuyerSession(

        buyer_id=buyer.id,

        token_hash=hash_token(
            token
        ),

        expires_at=expires_at,

        is_active=True,

    )

    db.add(
        session
    )

    await db.commit()

    return BuyerVerifyOTPResponse(

        message=(
            "Email verified successfully. "
            "Your buyer account is now active."
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
    response_model=BuyerRegisterResponse,
)
async def resend_buyer_otp(

    data: BuyerResendOTPRequest,

    db: AsyncSession = Depends(
        get_db
    ),

):

    email = (
        str(data.email)
        .lower()
        .strip()
    )

    result = await db.execute(

        select(Buyer)

        .where(
            Buyer.email == email
        )

    )

    buyer = (
        result.scalar_one_or_none()
    )

    if buyer is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "BUYER_NOT_FOUND",
                "message": (
                    "Buyer account not found."
                ),
            },
        )

    if buyer.is_email_verified:

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
    # Create OTP
    # ==========================================

    try:

        otp = await create_buyer_otp(
            db,
            buyer.id,
        )

        await db.commit()

    except HTTPException:

        await db.rollback()

        raise

    # ==========================================
    # Send OTP
    # ==========================================

    try:

        await send_buyer_otp_email(
            email=buyer.email,
            buyer_name=buyer.name,
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

    return BuyerRegisterResponse(

        message=(
            "A new verification OTP "
            "has been sent."
        ),

        email=buyer.email,

    )


# ==================================================
# LOGIN
# ==================================================

@router.post(
    "/login",
    response_model=BuyerLoginResponse,
)
async def buyer_login(

    data: BuyerLoginRequest,

    db: AsyncSession = Depends(
        get_db
    ),

):

    email = (
        str(data.email)
        .lower()
        .strip()
    )

    # ==========================================
    # Find buyer
    # ==========================================

    result = await db.execute(

        select(Buyer)

        .where(
            Buyer.email == email
        )

    )

    buyer = (
        result.scalar_one_or_none()
    )

    # ==========================================
    # Credentials
    # ==========================================

    if (
        buyer is None
        or not verify_password(
            data.password,
            buyer.password_hash,
        )
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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

    if not buyer.is_email_verified:

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

    if not buyer.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_INACTIVE",
                "message": (
                    "Buyer account is inactive."
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
        uid=str(buyer.id),
    )

    # ==========================================
    # Store session
    # ==========================================

    session = BuyerSession(

        buyer_id=buyer.id,

        token_hash=hash_token(
            token
        ),

        expires_at=expires_at,

        is_active=True,

    )

    db.add(
        session
    )

    await db.commit()

    return BuyerLoginResponse(

        access_token=token,

        token_type="bearer",

        expires_at=expires_at,

    )


# ==================================================
# ME
# ==================================================

@router.get(
    "/me",
    response_model=BuyerMeResponse,
)
async def buyer_me(

    buyer: Buyer = Depends(
        get_current_buyer
    ),

):

    return buyer


# ==================================================
# LOGOUT
# ==================================================

@router.post(
    "/logout",
)
async def buyer_logout(

    request: Request,

    buyer: Buyer = Depends(
        get_current_buyer
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
            status_code=status.HTTP_401_UNAUTHORIZED,
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header.",
        )

    # ==========================================
    # Find session
    # ==========================================

    token_hash = hash_token(
        token
    )

    result = await db.execute(

        select(BuyerSession)

        .where(

            BuyerSession.buyer_id
            == buyer.id,

            BuyerSession.token_hash
            == token_hash,

            BuyerSession.is_active.is_(True),

        )

    )

    session = (
        result.scalar_one_or_none()
    )

    if session:

        session.is_active = False

        await db.commit()

    return {
        "message": (
            "Buyer logged out successfully."
        )
    }