from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.buyer.buyer_saved_product import BuyerSavedProduct
from app.models.seller.product.product import SellerProduct


async def get_saved_products(
    db: AsyncSession,
    buyer_id: int,
):
    result = await db.execute(
        select(BuyerSavedProduct)
        .where(BuyerSavedProduct.buyer_id == buyer_id)
        .options(
            selectinload(BuyerSavedProduct.product)
        )
        .order_by(
            BuyerSavedProduct.created_at.desc()
        )
    )

    return result.scalars().all()


async def is_product_saved(
    db: AsyncSession,
    buyer_id: int,
    product_id: int,
) -> bool:
    result = await db.execute(
        select(BuyerSavedProduct.id)
        .where(
            BuyerSavedProduct.buyer_id == buyer_id,
            BuyerSavedProduct.product_id == product_id,
        )
    )

    return result.scalar_one_or_none() is not None


async def save_product(
    db: AsyncSession,
    buyer_id: int,
    product_id: int,
):
    # Make sure product exists
    product_result = await db.execute(
        select(SellerProduct).where(
            SellerProduct.id == product_id
        )
    )

    product = product_result.scalar_one_or_none()

    if product is None:
        return None, "Product not found."

    # Already saved
    existing_result = await db.execute(
        select(BuyerSavedProduct)
        .where(
            BuyerSavedProduct.buyer_id == buyer_id,
            BuyerSavedProduct.product_id == product_id,
        )
    )

    existing = existing_result.scalar_one_or_none()

    if existing:
        return existing, "Product is already saved."

    # Save new product without capacity restrictions
    saved_product = BuyerSavedProduct(
        buyer_id=buyer_id,
        product_id=product_id,
    )

    db.add(saved_product)

    await db.commit()

    # Load product relationship
    result = await db.execute(
        select(BuyerSavedProduct)
        .where(
            BuyerSavedProduct.id == saved_product.id
        )
        .options(
            selectinload(BuyerSavedProduct.product)
        )
    )

    saved_product = result.scalar_one()

    return saved_product, "Product saved successfully."


async def remove_saved_product(
    db: AsyncSession,
    buyer_id: int,
    product_id: int,
) -> bool:
    result = await db.execute(
        select(BuyerSavedProduct)
        .where(
            BuyerSavedProduct.buyer_id == buyer_id,
            BuyerSavedProduct.product_id == product_id,
        )
    )

    saved_product = result.scalar_one_or_none()

    if saved_product is None:
        return False

    await db.delete(saved_product)
    await db.commit()

    return True