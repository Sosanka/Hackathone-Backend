from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.models.buyer.buyer import Buyer
from app.models.seller.product.product import SellerProduct

from app.schemas.buyer.saved_items import (
    SavedItemOut,
    SavedItemToggleResponse,
)

from app.services.buyer.auth import get_current_buyer

from app.services.buyer.saved_items import (
    get_saved_items_with_products,
    get_saved_product_ids,
    remove_saved_item,
    toggle_saved_item,
)


router = APIRouter(
    prefix="/buyer/saved-items",
    tags=["Buyer Saved Items"],
)


@router.get(
    "/",
    response_model=list[SavedItemOut],
)
async def list_saved_items(

    buyer: Buyer = Depends(get_current_buyer),

    db: AsyncSession = Depends(get_db),

):

    rows = await get_saved_items_with_products(
        db,
        buyer.id,
    )

    return [

        SavedItemOut(

            id=saved.id,

            product_id=product.id,

            created_at=saved.created_at,

            product_name=product.product_name,

            price_per_unit=product.price_per_unit,

            unit=product.unit,

            image_url=getattr(product, "image_url", None),

            seller_id=getattr(product, "seller_id", None),

            location_name=getattr(product, "location_name", None),

        )

        for saved, product in rows

    ]


@router.get(
    "/ids",
    response_model=list[int],
)
async def list_saved_item_ids(

    buyer: Buyer = Depends(get_current_buyer),

    db: AsyncSession = Depends(get_db),

):

    return await get_saved_product_ids(
        db,
        buyer.id,
    )


@router.post(
    "/{product_id}/toggle",
    response_model=SavedItemToggleResponse,
)
async def toggle_saved_item_route(

    product_id: int,

    buyer: Buyer = Depends(get_current_buyer),

    db: AsyncSession = Depends(get_db),

):

    result = await db.execute(

        select(SellerProduct.id)

        .where(
            SellerProduct.id == product_id
        )

    )

    if result.scalar_one_or_none() is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PRODUCT_NOT_FOUND",
                "message": "Product not found.",
            },
        )

    saved = await toggle_saved_item(
        db,
        buyer.id,
        product_id,
    )

    return SavedItemToggleResponse(

        saved=saved,

        product_id=product_id,

    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_saved_item_route(

    product_id: int,

    buyer: Buyer = Depends(get_current_buyer),

    db: AsyncSession = Depends(get_db),

):

    removed = await remove_saved_item(
        db,
        buyer.id,
        product_id,
    )

    if not removed:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SAVED_ITEM_NOT_FOUND",
                "message": "Saved item not found.",
            },
        )

    return None