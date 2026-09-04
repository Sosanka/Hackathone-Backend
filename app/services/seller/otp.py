from datetime import (
    datetime,
    timedelta,
    timezone,
)

from fastapi import HTTPException, status
from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    generate_otp,
    hash_token,
)
from app.models.seller.seller_otp import (
    SellerEmailOTP,
)


async def create_seller_otp(
    db: AsyncSession,
    seller_id: int,
) -> str:

    now = datetime.now(
        timezone.utc
    )

    # ==========================================
    # Check resend cooldown
    # ==========================================

    result = await db.execute(
        select(SellerEmailOTP)
        .where(
            SellerEmailOTP.seller_id
            == seller_id,
        )
        .order_by(
            SellerEmailOTP.created_at.desc()
        )
        .limit(1)
    )

    latest = result.scalar_one_or_none()

    if latest:

        cooldown = (
            now - latest.created_at
        ).total_seconds()

        if (
            cooldown
            < settings.SELLER_OTP_RESEND_COOLDOWN_SECONDS
        ):

            remaining = int(
                settings.SELLER_OTP_RESEND_COOLDOWN_SECONDS
                - cooldown
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "OTP_COOLDOWN",
                    "message": (
                        f"Please wait {remaining} "
                        "seconds before requesting another OTP."
                    ),
                    "retry_after": remaining,
                },
            )

    # ==========================================
    # Invalidate previous OTPs
    # ==========================================

    await db.execute(
        update(SellerEmailOTP)
        .where(
            SellerEmailOTP.seller_id
            == seller_id,

            SellerEmailOTP.is_used.is_(False),
        )
        .values(
            is_used=True
        )
    )

    # ==========================================
    # Generate OTP
    # ==========================================

    otp = generate_otp()

    # ==========================================
    # Store hash
    # ==========================================

    record = SellerEmailOTP(

        seller_id=seller_id,

        otp_hash=hash_token(
            otp
        ),

        expires_at=(
            now
            + timedelta(
                minutes=(
                    settings.SELLER_OTP_EXPIRE_MINUTES
                )
            )
        ),

        attempts=0,

        is_used=False,
    )

    db.add(record)

    await db.flush()

    return otp