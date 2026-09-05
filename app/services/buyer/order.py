from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer.order import BuyerOrder
from app.models.seller.product.product import SellerProduct

from app.schemas.buyer.order.request import (
    OrderCreateSchema,
)
from app.schemas.buyer.order.response import (
    StockCheckResponse,
)


# ==========================================================
# CHECK STOCK
# ==========================================================

async def check_product_stock(
    db: AsyncSession,
    product_id: int,
    requested_quantity: Decimal,
) -> StockCheckResponse:

    # ------------------------------------------------------
    # GET ACTIVE PRODUCT
    # ------------------------------------------------------

    result = await db.execute(
        select(SellerProduct)
        .where(
            SellerProduct.id == product_id,
            SellerProduct.status == "active",
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or no longer available",
        )

    # ------------------------------------------------------
    # CHECK STOCK
    # ------------------------------------------------------

    available = (
        product.quantity >= requested_quantity
    )

    if not available:
        return StockCheckResponse(
            product_id=product.id,
            requested_quantity=requested_quantity,
            available_quantity=product.quantity,
            unit=product.unit,
            available=False,
            message=(
                f"Not enough stock. "
                f"Only {product.quantity} "
                f"{product.unit} available."
            ),
        )

    # ------------------------------------------------------
    # AVAILABLE
    # ------------------------------------------------------

    return StockCheckResponse(
        product_id=product.id,
        requested_quantity=requested_quantity,
        available_quantity=product.quantity,
        unit=product.unit,
        available=True,
        message=(
            f"Stock available. "
            f"{product.quantity} "
            f"{product.unit} currently available."
        ),
    )


# ==========================================================
# CREATE ORDER
# ==========================================================

async def create_order(
    db: AsyncSession,
    buyer_id: int,
    data: OrderCreateSchema,
) -> BuyerOrder:

    # ======================================================
    # IMPORTANT
    # ======================================================
    #
    # SELECT FOR UPDATE locks the product row.
    #
    # This prevents:
    #
    # Buyer A -> sees 10 kg
    # Buyer B -> sees 10 kg
    # Buyer A -> buys 8 kg
    # Buyer B -> buys 8 kg
    #
    # Instead, requests are processed safely.
    # ======================================================

    result = await db.execute(
        select(SellerProduct)
        .where(
            SellerProduct.id == data.product_id,
            SellerProduct.status == "active",
        )
        .with_for_update()
    )

    product = result.scalar_one_or_none()

    # ------------------------------------------------------
    # PRODUCT NOT FOUND
    # ------------------------------------------------------

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found or no longer available",
        )

    # ------------------------------------------------------
    # FINAL STOCK CHECK
    # ------------------------------------------------------
    # Never trust the previous /stock request.
    # Stock may have changed after that request.
    # ------------------------------------------------------

    if product.quantity < data.quantity:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Not enough stock",
                "product_id": product.id,
                "requested_quantity": str(
                    data.quantity
                ),
                "available_quantity": str(
                    product.quantity
                ),
                "unit": product.unit,
            },
        )

    # ======================================================
    # CALCULATE PRICE
    # ======================================================

    total_price = (
        data.quantity *
        product.price_per_unit
    )

    # ======================================================
    # DECREASE STOCK
    # ======================================================

    product.quantity = (
        product.quantity -
        data.quantity
    )

    # ------------------------------------------------------
    # IF STOCK BECOMES ZERO
    # ------------------------------------------------------

    if product.quantity == 0:

        product.status = "out_of_stock"

    # ======================================================
    # CREATE ORDER
    # ======================================================

    order = BuyerOrder(

        buyer_id=buyer_id,

        product_id=product.id,

        seller_id=product.seller_id,

        # Product snapshot
        product_name=product.product_name,

        quantity=data.quantity,

        unit=product.unit,

        price_per_unit=product.price_per_unit,

        total_price=total_price,

        # Customer
        customer_name=data.customer_name,

        customer_phone=data.customer_phone,

        # Location
        location_name=data.location_name,

        delivery_address=data.delivery_address,

        latitude=data.latitude,

        longitude=data.longitude,

        # Status
        status="placed",
    )

    db.add(order)

    # ======================================================
    # COMMIT
    # ======================================================

    try:

        await db.commit()

        await db.refresh(order)

    except Exception:

        await db.rollback()

        raise

    return order


# ==========================================================
# GET BUYER ORDERS
# ==========================================================

async def get_buyer_orders(
    db: AsyncSession,
    buyer_id: int,
) -> list[BuyerOrder]:

    result = await db.execute(
        select(BuyerOrder)
        .where(
            BuyerOrder.buyer_id == buyer_id
        )
        .order_by(
            BuyerOrder.created_at.desc()
        )
    )

    return list(
        result.scalars().all()
    )


# ==========================================================
# GET SINGLE BUYER ORDER
# ==========================================================

async def get_buyer_order_by_id(
    db: AsyncSession,
    buyer_id: int,
    order_id: int,
) -> BuyerOrder:

    result = await db.execute(
        select(BuyerOrder)
        .where(
            BuyerOrder.id == order_id,
            BuyerOrder.buyer_id == buyer_id,
        )
    )

    order = result.scalar_one_or_none()

    if not order:

        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return order