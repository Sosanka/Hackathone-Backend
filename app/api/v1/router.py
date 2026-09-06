from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router

from app.api.v1.seller.auth import router as seller_auth_router
from app.api.v1.seller.account.router import (
    router as seller_account_router,
)
from app.api.v1.seller.product.router import (
    router as seller_product_router,
)

from app.api.v1.buyer.auth import router as buyer_auth_router
from app.api.v1.buyer.product.public_router import (
    router as public_product_router,
)

from app.api.v1.buyer.saved_product.router import (
    router as buyer_saved_products_router,
)

from app.api.v1.buyer.save_items import router as buyer_saved_items_router

from app.api.v1.buyer.order.router import (
    router as buyer_order_router,
)

from app.api.v1.buyer.cart.router import router as buyer_cart_router


router = APIRouter(
    prefix="/api/v1",
)


# ============================================================
# GENERAL AUTH
# ============================================================

router.include_router(
    auth_router,
)


router.include_router(
    buyer_cart_router
)

router.include_router(
    buyer_saved_products_router
)   

# ============================================================
# SELLER AUTH & MANAGEMENT
# ============================================================

router.include_router(
    seller_auth_router,
)

router.include_router(
    seller_account_router,
    prefix="/seller",
)

router.include_router(
    seller_product_router,
    prefix="/seller",
)


# ============================================================
# BUYER & PUBLIC ENDPOINTS
# ============================================================

router.include_router(
    buyer_auth_router,
)

# Public products endpoint: /api/v1/products
router.include_router(
    public_product_router,
)

router.include_router(
    buyer_saved_items_router,
    prefix="/buyer",
)

router.include_router(
    buyer_order_router,
    prefix="/buyer",
)