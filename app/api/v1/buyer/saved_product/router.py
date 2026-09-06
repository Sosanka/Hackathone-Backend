from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.buyer.auth import get_current_buyer

from app.schemas.buyer.saved_products import (
    SavedProductCreateSchema,
    SavedProductResponseSchema,
    SavedProductToggleResponseSchema,
)

from app.services.buyer.saved_products import (
    get_saved_products,
    is_product_saved,
    remove_saved_product,
    save_product,
)


router = APIRouter(
    prefix="/buyer/saved-products",
    tags=["Buyer Saved Products"],
)


@router.get(
    "",
    response_model=list[SavedProductResponseSchema],
)
async def get_my_saved_products(
    db: AsyncSession = Depends(get_db),
    buyer=Depends(get_current_buyer),
):
    return await get_saved_products(
        db=db,
        buyer_id=buyer.id,
    )


@router.get(
    "/{product_id}/status",
    response_model=SavedProductToggleResponseSchema,
)
async def get_saved_status(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    buyer=Depends(get_current_buyer),
):
    saved = await is_product_saved(
        db=db,
        buyer_id=buyer.id,
        product_id=product_id,
    )

    return {
        "product_id": product_id,
        "saved": saved,
        "message": "Product is saved."
        if saved
        else "Product is not saved.",
    }


@router.post(
    "",
    response_model=SavedProductToggleResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def save_product_for_later(
    data: SavedProductCreateSchema,
    db: AsyncSession = Depends(get_db),
    buyer=Depends(get_current_buyer),
):
    saved_product, message = await save_product(
        db=db,
        buyer_id=buyer.id,
        product_id=data.product_id,
    )

    if saved_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )

    return {
        "product_id": data.product_id,
        "saved": True,
        "message": message,
    }


@router.delete(
    "/{product_id}",
    response_model=SavedProductToggleResponseSchema,
)
async def delete_saved_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    buyer=Depends(get_current_buyer),
):
    removed = await remove_saved_product(
        db=db,
        buyer_id=buyer.id,
        product_id=product_id,
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product is not saved.",
        )

    return {
        "product_id": product_id,
        "saved": False,
        "message": "Product removed from saved items.",
    }