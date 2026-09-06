from decimal import Decimal

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.buyer.auth import get_current_buyer
from app.core.database import get_db

from app.schemas.buyer.saved_items import (
    CartAddRequest,
    CartItemResponse,
    CartUpdateRequest,
)

from app.services.buyer.saved_items import (
    add_to_cart,
    get_cart,
    remove_from_cart,
    update_cart_item,
)


router = APIRouter(
    prefix="/buyer/cart",
    tags=["Buyer Cart"],
)


@router.get(
    "",
    response_model=list[CartItemResponse],
)
async def get_buyer_cart(
    current_buyer=Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await get_cart(
        db=db,
        buyer_id=current_buyer.id,
    )


@router.post(
    "",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_cart_item(
    data: CartAddRequest,
    current_buyer=Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    item = await add_to_cart(
        db=db,
        buyer_id=current_buyer.id,
        product_id=data.product_id,
        quantity=data.quantity,
    )

    # Return complete cart item
    cart = await get_cart(
        db=db,
        buyer_id=current_buyer.id,
    )

    for cart_item in cart:
        if cart_item["product_id"] == data.product_id:
            return cart_item


@router.patch(
    "/{product_id}",
    response_model=CartItemResponse,
)
async def update_cart(
    product_id: int,
    data: CartUpdateRequest,
    current_buyer=Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    await update_cart_item(
        db=db,
        buyer_id=current_buyer.id,
        product_id=product_id,
        quantity=data.quantity,
    )

    cart = await get_cart(
        db=db,
        buyer_id=current_buyer.id,
    )

    for item in cart:
        if item["product_id"] == product_id:
            return item


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cart_item(
    product_id: int,
    current_buyer=Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    await remove_from_cart(
        db=db,
        buyer_id=current_buyer.id,
        product_id=product_id,
    )