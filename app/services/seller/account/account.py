from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seller.seller import Seller
from app.models.seller.account.seller_account import SellerAccount
from app.models.seller.account.store import SellerStore

from app.schemas.seller.account.request import (
    SellerAccountCreateRequest,
)

from app.services.seller.account.location import (
    validate_coordinates,
    validate_store_coordinates,
)


async def create_seller_account(
    db: AsyncSession,
    seller: Seller,
    data: SellerAccountCreateRequest,
) -> tuple[SellerAccount, SellerStore]:

    # ==========================================
    # SELLER STATUS
    # ==========================================

    if not seller.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller account is inactive.",
        )

    # ==========================================
    # EMAIL VERIFICATION
    # ==========================================

    if not seller.is_email_verified:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller email is not verified.",
        )

    # ==========================================
    # VALIDATE SELLER LOCATION
    # ==========================================

    try:

        validate_coordinates(
            data.latitude,
            data.longitude,
        )

        validate_store_coordinates(
            data.store_latitude,
            data.store_longitude,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # ==========================================
    # CHECK ACCOUNT
    # ==========================================

    result = await db.execute(

        select(SellerAccount)

        .where(
            SellerAccount.seller_id
            == seller.id
        )

    )

    existing_account = (
        result.scalar_one_or_none()
    )

    if existing_account:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seller account already exists.",
        )

    # ==========================================
    # CREATE SELLER ACCOUNT
    # ==========================================

    account = SellerAccount(

        seller_id=seller.id,

        name=data.name,

        address_line=data.address_line,

        city=data.city,

        district=data.district,

        state=data.state,

        country=data.country,

        pincode=data.pincode,

        latitude=data.latitude,

        longitude=data.longitude,

        google_place_id=data.google_place_id,

        formatted_address=data.formatted_address,
    )

    db.add(account)

    await db.flush()

    # ==========================================
    # CREATE STORE
    # ==========================================

    store = SellerStore(

        seller_id=seller.id,

        store_name=data.store_name,

        description=data.store_description,

        store_phone=data.store_phone,

        address_line=data.store_address_line,

        city=data.store_city,

        district=data.store_district,

        state=data.store_state,

        country=data.store_country,

        pincode=data.store_pincode,

        latitude=data.store_latitude,

        longitude=data.store_longitude,

        google_place_id=(
            data.store_google_place_id
        ),

        formatted_address=(
            data.store_formatted_address
        ),

        is_active=True,
    )

    db.add(store)

    # ==========================================
    # COMMIT EVERYTHING
    # ==========================================

    await db.commit()

    await db.refresh(account)

    await db.refresh(store)

    return account, store