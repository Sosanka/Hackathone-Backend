from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
# from app.api.v1.health.router import router as health_router

from app.api.v1.seller.auth import router as seller_auth_router
from app.api.v1.seller.account.router import router as seller_account_router

from app.api.v1.buyer.auth import router as buyer_auth_router




router = APIRouter(
    prefix="/api/v1",
)





router.include_router(
    auth_router,
)




router.include_router(
    seller_auth_router,
)

router.include_router(
    seller_account_router,
    prefix="/seller",
)




router.include_router(
    buyer_auth_router,
)