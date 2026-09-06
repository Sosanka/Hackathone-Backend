from decimal import Decimal

from fastapi import HTTPException

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer.order import BuyerOrder
from app.models.seller.product.product import SellerProduct

from app.schemas.buyer.order.request import (
    CheckoutCreateSchema,
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
# CREATE SINGLE ORDER
# ==========================================================

async def create_order(
    db: AsyncSession,
    buyer_id: int,
    data,
) -> BuyerOrder:

    result = await db.execute(
        select(SellerProduct)
        .where(
            SellerProduct.id == data.product_id,
            SellerProduct.status == "active",
        )
        .with_for_update()
    )

    product = result.scalar_one_or_none()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found or no longer available",
        )

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

    total_price = (
        data.quantity *
        product.price_per_unit
    )

    product.quantity = (
        product.quantity -
        data.quantity
    )

    if product.quantity == 0:
        product.status = "out_of_stock"

    order = BuyerOrder(
        buyer_id=buyer_id,
        product_id=product.id,
        seller_id=product.seller_id,

        product_name=product.product_name,

        quantity=data.quantity,

        unit=product.unit,

        price_per_unit=product.price_per_unit,

        total_price=total_price,

        customer_name=data.customer_name,

        customer_phone=data.customer_phone,

        location_name=data.location_name,

        delivery_address=data.delivery_address,

        latitude=data.latitude,

        longitude=data.longitude,

        status="placed",
    )

    db.add(order)

    try:

        await db.commit()

        await db.refresh(order)

    except Exception:

        await db.rollback()

        raise

    return order


# ==========================================================
# CHECKOUT ENTIRE CART
# ==========================================================

async def checkout_cart(
    db: AsyncSession,
    buyer_id: int,
    data: CheckoutCreateSchema,
):
    """
    Create orders for every item currently
    present in the authenticated buyer's cart.

    The backend calculates prices from the database.
    """

    # ======================================================
    # IMPORT YOUR CART MODEL
    # ======================================================

    from app.models.buyer.buyer_saved_item import BuyerSavedItem

    # ------------------------------------------------------
    # IMPORTANT
    #
    # Replace BuyerSavedItem above with your actual
    # cart model if your cart uses a different model.
    # ------------------------------------------------------

    result = await db.execute(
        select(BuyerSavedItem)
        .where(
            BuyerSavedItem.buyer_id == buyer_id
        )
    )

    cart_items = list(
        result.scalars().all()
    )

    if not cart_items:

        raise HTTPException(
            status_code=400,
            detail="Your cart is empty",
        )

    # ======================================================
    # PAYMENT
    # ======================================================

    if data.payment_method != "cod":

        raise HTTPException(
            status_code=400,
            detail="Only Cash on Delivery is supported",
        )

    # ======================================================
    # CREATE ORDERS
    # ======================================================

    created_orders = []

    total_amount = Decimal("0")

    try:

        for cart_item in cart_items:

            # --------------------------------------------------
            # LOCK PRODUCT
            # --------------------------------------------------

            product_result = await db.execute(
                select(SellerProduct)
                .where(
                    SellerProduct.id ==
                    cart_item.product_id,

                    SellerProduct.status == "active",
                )
                .with_for_update()
            )

            product = (
                product_result
                .scalar_one_or_none()
            )

            if not product:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Product "
                        f"{cart_item.product_id} "
                        f"is no longer available."
                    ),
                )

            # --------------------------------------------------
            # STOCK CHECK
            # --------------------------------------------------

            if product.quantity < cart_item.quantity:

                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": (
                            f"Not enough stock for "
                            f"{product.product_name}"
                        ),
                        "product_id": product.id,
                        "requested_quantity": str(
                            cart_item.quantity
                        ),
                        "available_quantity": str(
                            product.quantity
                        ),
                        "unit": product.unit,
                    },
                )

            # --------------------------------------------------
            # CALCULATE PRICE FROM DATABASE
            # --------------------------------------------------

            item_total = (
                cart_item.quantity *
                product.price_per_unit
            )

            # --------------------------------------------------
            # DECREASE STOCK
            # --------------------------------------------------

            product.quantity = (
                product.quantity -
                cart_item.quantity
            )

            if product.quantity == 0:

                product.status = "out_of_stock"

            # --------------------------------------------------
            # CREATE ORDER
            # --------------------------------------------------

            order = BuyerOrder(

                buyer_id=buyer_id,

                product_id=product.id,

                seller_id=product.seller_id,

                product_name=product.product_name,

                quantity=cart_item.quantity,

                unit=product.unit,

                price_per_unit=product.price_per_unit,

                total_price=item_total,

                customer_name=data.customer_name,

                customer_phone=data.customer_phone,

                location_name=data.location_name,

                delivery_address=data.delivery_address,

                latitude=data.latitude,

                longitude=data.longitude,

                status="placed",
            )

            db.add(order)

            created_orders.append(order)

            total_amount += item_total

        # ==================================================
        # FLUSH ORDERS
        # ==================================================

        await db.flush()

        # ==================================================
        # CLEAR CART
        # ==================================================

        for cart_item in cart_items:

            await db.delete(cart_item)

        # ==================================================
        # COMMIT EVERYTHING TOGETHER
        # ==================================================

        await db.commit()

        # ==================================================
        # REFRESH ORDERS
        # ==================================================

        for order in created_orders:

            await db.refresh(order)

    except HTTPException:

        await db.rollback()

        raise

    except Exception:

        await db.rollback()

        raise

    return {
        "success": True,
        "payment_method": "cod",
        "message": "Order placed successfully",
        "order_ids": [
            order.id
            for order in created_orders
        ],
        "orders": created_orders,
        "total_amount": total_amount,
    }


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