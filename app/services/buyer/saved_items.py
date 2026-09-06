from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer.buyer_saved_item import BuyerSavedItem
from app.models.seller.product.product import SellerProduct


async def add_to_cart(
    db: AsyncSession,
    buyer_id: int,
    product_id: int,
    quantity: Decimal,
) -> BuyerSavedItem:
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero.",
        )

    # Verify product availability
    result = await db.execute(
        select(SellerProduct).where(
            SellerProduct.id == product_id,
            SellerProduct.status == "active",
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or unavailable.",
        )

    if quantity > product.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.quantity} {product.unit} available.",
        )

    # Check for existing item in saved items/cart
    result = await db.execute(
        select(BuyerSavedItem).where(
            BuyerSavedItem.buyer_id == buyer_id,
            BuyerSavedItem.product_id == product_id,
        )
    )
    item = result.scalar_one_or_none()

    if item:
        new_quantity = item.quantity + quantity
        if new_quantity > product.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product.quantity} {product.unit} available.",
            )
        item.quantity = new_quantity
    else:
        item = BuyerSavedItem(
            buyer_id=buyer_id,
            product_id=product_id,
            quantity=quantity,
        )
        db.add(item)

    await db.commit()
    await db.refresh(item)
    return item


async def get_cart(
    db: AsyncSession,
    buyer_id: int,
) -> list[dict]:
    result = await db.execute(
        select(BuyerSavedItem, SellerProduct)
        .join(
            SellerProduct,
            SellerProduct.id == BuyerSavedItem.product_id,
        )
        .where(
            BuyerSavedItem.buyer_id == buyer_id,
        )
        .order_by(BuyerSavedItem.created_at.desc())
    )
    rows = result.all()

    return [
        {
            "id": item.id,
            "product_id": product.id,
            "product_name": getattr(product, "product_name", getattr(product, "name", "")),
            "description": product.description,
            "category": getattr(product, "category", None),
            "image_url": getattr(product, "image_url", None),
            "quantity": item.quantity,
            "unit": getattr(product, "unit", "unit"),
            "price_per_unit": product.price_per_unit,
            "total_price": item.quantity * product.price_per_unit,
            "location_name": getattr(product, "location_name", None),
        }
        for item, product in rows
    ]


async def update_cart_item(
    db: AsyncSession,
    buyer_id: int,
    product_id: int,
    quantity: Decimal,
) -> BuyerSavedItem:
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero.",
        )

    result = await db.execute(
        select(BuyerSavedItem).where(
            BuyerSavedItem.buyer_id == buyer_id,
            BuyerSavedItem.product_id == product_id,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found.",
        )

    result = await db.execute(
        select(SellerProduct).where(
            SellerProduct.id == product_id,
            SellerProduct.status == "active",
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product no longer available.",
        )

    if quantity > product.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.quantity} {product.unit} available.",
        )

    item.quantity = quantity
    await db.commit()
    await db.refresh(item)
    return item


async def remove_from_cart(
    db: AsyncSession,
    buyer_id: int,
    product_id: int,
) -> bool:
    result = await db.execute(
        select(BuyerSavedItem).where(
            BuyerSavedItem.buyer_id == buyer_id,
            BuyerSavedItem.product_id == product_id,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found.",
        )

    await db.delete(item)
    await db.commit()
    return True


async def toggle_saved_item(
    db: AsyncSession,
    buyer_id: int,
    product_id: int,
) -> dict:
    result = await db.execute(
        select(BuyerSavedItem).where(
            BuyerSavedItem.buyer_id == buyer_id,
            BuyerSavedItem.product_id == product_id,
        )
    )
    item = result.scalar_one_or_none()

    if item:
        await db.delete(item)
        await db.commit()
        return {"saved": False, "message": "Item removed from saved items."}

    result = await db.execute(
        select(SellerProduct).where(
            SellerProduct.id == product_id,
            SellerProduct.status == "active",
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or unavailable.",
        )

    new_item = BuyerSavedItem(
        buyer_id=buyer_id,
        product_id=product_id,
        quantity=Decimal("1"),
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return {"saved": True, "message": "Item saved successfully.", "item_id": new_item.id}


# Router Compatibility Functions
get_saved_items_with_products = get_cart
remove_saved_item = remove_from_cart


async def get_saved_product_ids(db: AsyncSession, buyer_id: int) -> List[int]:
    result = await db.execute(
        select(BuyerSavedItem.product_id).where(
            BuyerSavedItem.buyer_id == buyer_id
        )
    )
    return list(result.scalars().all())