import secrets

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_token

from app.models.buyer.buyer_otp import (
    BuyerEmailOTP,
)


async def create_buyer_otp(
    db: AsyncSession,
    buyer_id: int,
):

    now = datetime.now(
        timezone.utc
    )

    # ==========================================
    # Latest OTP
    # ==========================================

    result = await db.execute(

        select(BuyerEmailOTP)

        .where(
            BuyerEmailOTP.buyer_id
            == buyer_id
        )

        .order_by(
            BuyerEmailOTP.created_at.desc()
        )

        .limit(1)

    )

    latest_otp = (
        result.scalar_one_or_none()
    )

    # ==========================================
    # Resend cooldown
    # ==========================================

    if latest_otp:

        created_at = latest_otp.created_at

        if created_at.tzinfo is None:

            created_at = created_at.replace(
                tzinfo=timezone.utc
            )

        elapsed = (
            now - created_at
        ).total_seconds()

        cooldown = (
            settings
            .BUYER_OTP_RESEND_COOLDOWN_SECONDS
        )

        if elapsed < cooldown:

            retry_after = int(
                cooldown - elapsed
            )

            raise HTTPException(
                status_code=(
                    status.HTTP_429_TOO_MANY_REQUESTS
                ),
                detail={
                    "code": "OTP_RESEND_COOLDOWN",
                    "message": (
                        "Please wait before "
                        "requesting another OTP."
                    ),
                    "retry_after": retry_after,
                },
            )

    # ==========================================
    # Invalidate previous OTPs
    # ==========================================

    result = await db.execute(

        select(BuyerEmailOTP)

        .where(

            BuyerEmailOTP.buyer_id
            == buyer_id,

            BuyerEmailOTP.is_used.is_(False),

        )

    )

    active_otps = (
        result.scalars().all()
    )

    for record in active_otps:

        record.is_used = True

    # ==========================================
    # Generate OTP
    # ==========================================

    otp = f"{secrets.randbelow(1000000):06d}"

    # ==========================================
    # Create OTP record
    # ==========================================

    otp_record = BuyerEmailOTP(

        buyer_id=buyer_id,

        otp_hash=hash_token(
            otp
        ),

        expires_at=(
            now
            + timedelta(
                minutes=(
                    settings
                    .BUYER_OTP_EXPIRE_MINUTES
                )
            )
        ),

        attempts=0,

        is_used=False,

    )

    db.add(
        otp_record
    )

    await db.flush()

    return otp