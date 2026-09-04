from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.seller.seller import Seller

from app.schemas.seller.account.request import (
    SellerAccountCreateRequest,
)

from app.schemas.seller.account.response import (
    SellerAccountCreateResponse,
    SellerLocationResponse,
    StoreResponse,
)

from app.services.seller.account.account import (
    create_seller_account,
)

from app.services.seller.auth import (
    get_current_seller,
)


router = APIRouter(
    prefix="/account",
    tags=["Seller Account"],
)


@router.post(
    "/create",
    response_model=SellerAccountCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_account(
    data: SellerAccountCreateRequest,
    current_seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):

    print("\n====================================")
    print("CREATE SELLER ACCOUNT CALLED")
    print("SELLER ID:", current_seller.id)
    print("SELLER EMAIL:", current_seller.email)
    print("====================================\n")

    account, store = await create_seller_account(
        db=db,
        seller=current_seller,
        data=data,
    )

    return SellerAccountCreateResponse(
        message="Seller account and store created successfully.",
        seller_id=current_seller.id,
        account_id=account.id,
        name=account.name,
        email=current_seller.email,
        phone=current_seller.phone,

        location=SellerLocationResponse(
            latitude=account.latitude,
            longitude=account.longitude,
            google_place_id=account.google_place_id,
            formatted_address=account.formatted_address,
        ),

        store=StoreResponse(
            id=store.id,
            store_name=store.store_name,
            description=store.description,
            store_phone=store.store_phone,
            address_line=store.address_line,
            city=store.city,
            district=store.district,
            state=store.state,
            country=store.country,
            pincode=store.pincode,
            latitude=store.latitude,
            longitude=store.longitude,
            google_place_id=store.google_place_id,
            formatted_address=store.formatted_address,
            is_active=store.is_active,
        ),

        created_at=account.created_at,
    )