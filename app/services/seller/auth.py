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

from app.models.seller.seller import Seller
from app.models.seller.seller_session import (
    SellerSession,
)


async def get_current_seller(

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

        select(SellerSession)

        .where(

            SellerSession.token_hash
            == token_hash,

            SellerSession.is_active.is_(True),

        )

    )

    session = (
        result.scalar_one_or_none()
    )

    if session is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or has been revoked.",
        )

    # ==========================================
    # Check expiration
    # ==========================================

    now = datetime.now(
        timezone.utc
    )

    if session.expires_at <= now:

        session.is_active = False

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired.",
        )

    # ==========================================
    # Find seller
    # ==========================================

    result = await db.execute(

        select(Seller)

        .where(

            Seller.id
            == session.seller_id,

            Seller.is_active.is_(True),

        )

    )

    seller = (
        result.scalar_one_or_none()
    )

    if seller is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seller account is unavailable.",
        )

    # ==========================================
    # Update session
    # ==========================================

    session.last_used_at = now

    await db.commit()

    return seller