from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.buyer.auth import (
    get_current_buyer,
)
from app.core.database import get_db
from app.schemas.buyer.order.request import (
    CheckoutCreateSchema,
    OrderCreateSchema,
    StockCheckRequest,
)
from app.schemas.buyer.order.response import (
    CheckoutResponseSchema,
    OrderResponseSchema,
    StockCheckResponse,
)
from app.services.buyer.order import (
    check_product_stock,
    checkout_cart,
    create_order,
    get_buyer_order_by_id,
    get_buyer_orders,
)

# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/orders",
    tags=["Buyer Orders"],
)


# ============================================================
# CHECK PRODUCT STOCK
# ============================================================
#
# GET /api/v1/buyer/orders/products/{product_id}/stock
#
# Example:
# /api/v1/buyer/orders/products/10/stock?quantity=5
# ============================================================

@router.get(
    "/products/{product_id}/stock",
    response_model=StockCheckResponse,
)
async def check_stock(
    product_id: int,
    stock_query: StockCheckRequest = Depends(),
    db: AsyncSession = Depends(get_db),
    buyer=Depends(get_current_buyer),
):
    """
    Check whether requested product quantity
    is currently available.
    """
    return await check_product_stock(
        db=db,
        product_id=product_id,
        requested_quantity=stock_query.quantity,
    )


# ============================================================
# CREATE ORDER
# ============================================================
#
# POST /api/v1/buyer/orders
#
# LOGIN REQUIRED
# ============================================================

@router.post(
    "",
    response_model=OrderResponseSchema,
    status_code=201,
)
async def create_buyer_order(
    data: OrderCreateSchema,
    db: AsyncSession = Depends(get_db),
    buyer=Depends(get_current_buyer),
):
    """
    Create an order.

    The buyer does not send buyer_id.
    buyer_id comes from the authenticated JWT.
    """
    return await create_order(
        db=db,
        buyer_id=buyer.id,
        data=data,
    )


# ============================================================
# CHECKOUT CART
# ============================================================
#
# POST /api/v1/buyer/orders/checkout
#
# LOGIN REQUIRED
# ============================================================

@router.post(
    "/checkout",
    response_model=CheckoutResponseSchema,
    status_code=201,
)
async def checkout_buyer_cart(
    data: CheckoutCreateSchema,
    db: AsyncSession = Depends(get_db),
    buyer=Depends(get_current_buyer),
):
    """
    Checkout the authenticated buyer's entire cart.

    Payment method is currently Cash on Delivery.
    """
    return await checkout_cart(
        db=db,
        buyer_id=buyer.id,
        data=data,
    )


# ============================================================
# GET ALL BUYER ORDERS
# ============================================================
#
# GET /api/v1/buyer/orders
# ============================================================

@router.get(
    "",
    response_model=list[OrderResponseSchema],
)
async def get_orders(
    db: AsyncSession = Depends(get_db),
    buyer=Depends(get_current_buyer),
):
    """
    Return all orders belonging to
    the currently logged-in buyer.
    """
    return await get_buyer_orders(
        db=db,
        buyer_id=buyer.id,
    )


# ============================================================
# GET SINGLE ORDER
# ============================================================
#
# GET /api/v1/buyer/orders/{order_id}
# ============================================================

@router.get(
    "/{order_id}",
    response_model=OrderResponseSchema,
)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    buyer=Depends(get_current_buyer),
):
    """
    Return a single order belonging
    to the logged-in buyer.
    """
    return await get_buyer_order_by_id(
        db=db,
        buyer_id=buyer.id,
        order_id=order_id,
    )