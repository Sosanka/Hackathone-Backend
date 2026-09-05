from decimal import Decimal

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seller.product.product import SellerProduct
from app.schemas.seller.product.request import ProductCreateSchema
from app.services.seller.product.image import (
    delete_product_image,
    save_product_image,
)


async def create_product(
    db: AsyncSession,
    seller_id: int,
    data: ProductCreateSchema,
    image: UploadFile | None = None,
) -> SellerProduct:

    image_url = None

    # ----------------------------------------------------------
    # SAVE IMAGE
    # ----------------------------------------------------------

    if image:
        image_url = await save_product_image(image)

    # ----------------------------------------------------------
    # CALCULATE TOTAL PRICE
    # ----------------------------------------------------------

    total_price = (
        data.quantity * data.price_per_unit
    )

    # ----------------------------------------------------------
    # CREATE PRODUCT
    # ----------------------------------------------------------

    product = SellerProduct(
        seller_id=seller_id,

        product_name=data.product_name,
        description=data.description,
        category=data.category,

        image_url=image_url,

        quantity=data.quantity,
        unit=data.unit,

        price_per_unit=data.price_per_unit,
        total_price=total_price,

        location_name=data.location_name,
        address=data.address,

        latitude=data.latitude,
        longitude=data.longitude,

        harvest_date=data.harvest_date,
        best_before_date=data.best_before_date,

        status="active",
    )

    db.add(product)

    try:
        await db.commit()
        await db.refresh(product)

    except Exception:
        await db.rollback()

        if image_url:
            delete_product_image(image_url)

        raise

    return product


async def get_seller_products(
    db: AsyncSession,
    seller_id: int,
) -> list[SellerProduct]:

    result = await db.execute(
        select(SellerProduct)
        .where(
            SellerProduct.seller_id == seller_id
        )
        .order_by(
            SellerProduct.created_at.desc()
        )
    )

    return list(result.scalars().all())


async def get_product_by_id(
    db: AsyncSession,
    seller_id: int,
    product_id: int,
) -> SellerProduct:

    result = await db.execute(
        select(SellerProduct)
        .where(
            SellerProduct.id == product_id,
            SellerProduct.seller_id == seller_id,
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


async def delete_product(
    db: AsyncSession,
    seller_id: int,
    product_id: int,
) -> None:

    product = await get_product_by_id(
        db,
        seller_id,
        product_id,
    )

    image_url = product.image_url

    await db.delete(product)

    await db.commit()

    if image_url:
        delete_product_image(image_url)