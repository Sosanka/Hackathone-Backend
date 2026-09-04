from datetime import (
    datetime,
    timezone,
)

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)

from authx import TokenPayload

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.core.security import (
    hash_token,
    security,
)

from app.models.buyer.buyer import Buyer

from app.models.buyer.buyer_session import (
    BuyerSession,
)


async def get_current_buyer(

    request: Request,

    payload: TokenPayload = Depends(
        security.access_token_required
    ),

    db: AsyncSession = Depends(
        get_db
    ),

):

    # ==========================================
    # Authorization header
    # ==========================================

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
    # Hash JWT
    # ==========================================

    token_hash = hash_token(
        token
    )

    # ==========================================
    # Find session
    # ==========================================

    result = await db.execute(

        select(BuyerSession)

        .where(

            BuyerSession.token_hash
            == token_hash,

            BuyerSession.is_active.is_(True),

        )

    )

    session = (
        result.scalar_one_or_none()
    )

    if session is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Session is invalid "
                "or has been revoked."
            ),
        )

    # ==========================================
    # Check expiration
    # ==========================================

    now = datetime.now(
        timezone.utc
    )

    expires_at = session.expires_at

    if expires_at.tzinfo is None:

        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at <= now:

        session.is_active = False

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired.",
        )

    # ==========================================
    # Validate token owner
    # ==========================================

    try:

        token_buyer_id = int(
            payload.sub
        )

    except (
        TypeError,
        ValueError,
        AttributeError,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    if (
        token_buyer_id
        != session.buyer_id
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication session.",
        )

    # ==========================================
    # Find buyer
    # ==========================================

    result = await db.execute(

        select(Buyer)

        .where(

            Buyer.id
            == session.buyer_id,

            Buyer.is_active.is_(True),

        )

    )

    buyer = (
        result.scalar_one_or_none()
    )

    if buyer is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Buyer account is unavailable.",
        )

    # ==========================================
    # Update session
    # ==========================================

    session.last_used_at = now

    await db.commit()

    return buyer