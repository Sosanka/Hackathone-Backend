from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer.buyer_saved_item import BuyerSavedItem
from app.models.seller.product.product import SellerProduct


async def get_saved_product_ids(
    db: AsyncSession,
    buyer_id: int,
):

    result = await db.execute(

        select(BuyerSavedItem.product_id)

        .where(
            BuyerSavedItem.buyer_id == buyer_id
        )

    )

    return [row[0] for row in result.all()]


async def get_saved_items_with_products(
    db: AsyncSession,
    buyer_id: int,
):

    result = await db.execute(

        select(BuyerSavedItem, SellerProduct)

        .join(
            SellerProduct,
            BuyerSavedItem.product_id == SellerProduct.id,
        )

        .where(
            BuyerSavedItem.buyer_id == buyer_id
        )

        .order_by(
            BuyerSavedItem.created_at.desc()
        )

    )

    return result.all()


async def toggle_saved_item(
    db: AsyncSession,
    buyer_id: int,
    product_id: int,
):

    result = await db.execute(

        select(BuyerSavedItem)

        .where(

            BuyerSavedItem.buyer_id == buyer_id,

            BuyerSavedItem.product_id == product_id,

        )

    )

    existing = result.scalar_one_or_none()

    if existing:

        await db.delete(existing)

        await db.commit()

        return False

    new_saved = BuyerSavedItem(

        buyer_id=buyer_id,

        product_id=product_id,

    )

    db.add(new_saved)

    try:

        await db.commit()

    except IntegrityError:

        await db.rollback()

        return True

    return True


async def remove_saved_item(
    db: AsyncSession,
    buyer_id: int,
    product_id: int,
):

    result = await db.execute(

        select(BuyerSavedItem)

        .where(

            BuyerSavedItem.buyer_id == buyer_id,

            BuyerSavedItem.product_id == product_id,

        )

    )

    existing = result.scalar_one_or_none()

    if existing is None:

        return False

    await db.delete(existing)

    await db.commit()

    return True