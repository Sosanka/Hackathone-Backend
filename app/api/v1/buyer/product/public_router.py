from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.seller.product.product import SellerProduct
from app.schemas.seller.product.response import ProductResponseSchema


router = APIRouter(
    prefix="/products",
    tags=["Public Products"],
)


@router.get(
    "",
    response_model=list[ProductResponseSchema],
)
async def get_public_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: str | None = Query(None),

    db: AsyncSession = Depends(get_db),
):

    query = select(SellerProduct)

    if category:
        query = query.where(
            SellerProduct.category == category
        )

    query = (
        query
        .order_by(
            SellerProduct.created_at.desc()
        )
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)

    return list(result.scalars().all())


@router.get(
    "/{product_id}",
    response_model=ProductResponseSchema,
)
async def get_public_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(SellerProduct)
        .where(
            SellerProduct.id == product_id
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product