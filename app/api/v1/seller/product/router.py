from datetime import date
from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.seller.auth import get_current_seller
from app.core.database import get_db

from app.schemas.seller.product.request import (
    ProductCreateSchema,
)
from app.schemas.seller.product.response import (
    ProductResponseSchema,
)

from app.services.seller.product.product import (
    create_product,
    delete_product,
    get_product_by_id,
    get_seller_products,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/products",
    tags=["Seller Products"],
)


# ============================================================
# CREATE PRODUCT
# ============================================================
# LOGIN REQUIRED
#
# POST /api/v1/seller/products
#
# Seller must send:
# Authorization: Bearer <seller_access_token>
# ============================================================

@router.post(
    "",
    response_model=ProductResponseSchema,
    status_code=201,
)
async def create_seller_product(
    # --------------------------------------------------------
    # PRODUCT INFORMATION
    # --------------------------------------------------------

    product_name: str = Form(...),

    description: str | None = Form(None),

    category: str | None = Form(None),

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    quantity: Decimal = Form(...),

    unit: str = Form(...),

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    price_per_unit: Decimal = Form(...),

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    location_name: str | None = Form(None),

    address: str | None = Form(None),

    latitude: Decimal | None = Form(None),

    longitude: Decimal | None = Form(None),

    # --------------------------------------------------------
    # DATES
    # --------------------------------------------------------

    harvest_date: date | None = Form(None),

    best_before_date: date | None = Form(None),

    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    image: UploadFile | None = File(None),

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    db: AsyncSession = Depends(get_db),

    # --------------------------------------------------------
    # SELLER AUTHENTICATION
    # --------------------------------------------------------
    # This makes login mandatory.
    # seller.id comes from the authenticated seller JWT.
    # Seller cannot send/change seller_id from frontend.
    # --------------------------------------------------------

    seller=Depends(get_current_seller),
):
    """
    Create a new product listing.

    Only authenticated sellers can create products.
    """

    # --------------------------------------------------------
    # VALIDATE REQUEST DATA
    # --------------------------------------------------------

    data = ProductCreateSchema(
        product_name=product_name.strip(),

        description=description,

        category=category,

        quantity=quantity,

        unit=unit,

        price_per_unit=price_per_unit,

        location_name=location_name,

        address=address,

        latitude=latitude,

        longitude=longitude,

        harvest_date=harvest_date,

        best_before_date=best_before_date,
    )

    # --------------------------------------------------------
    # CREATE PRODUCT
    # --------------------------------------------------------
    # seller_id comes ONLY from authenticated seller.
    # --------------------------------------------------------

    product = await create_product(
        db=db,

        seller_id=seller.id,

        data=data,

        image=image,
    )

    return product


# ============================================================
# GET ALL PRODUCTS OF LOGGED-IN SELLER
# ============================================================
#
# GET /api/v1/seller/products
#
# LOGIN REQUIRED
# ============================================================

@router.get(
    "",
    response_model=list[ProductResponseSchema],
)
async def get_products(
    db: AsyncSession = Depends(get_db),

    seller=Depends(get_current_seller),
):
    """
    Return only products belonging to the logged-in seller.
    """

    return await get_seller_products(
        db=db,

        seller_id=seller.id,
    )


# ============================================================
# GET SINGLE PRODUCT
# ============================================================
#
# GET /api/v1/seller/products/{product_id}
#
# LOGIN REQUIRED
# ============================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponseSchema,
)
async def get_product(
    product_id: int,

    db: AsyncSession = Depends(get_db),

    seller=Depends(get_current_seller),
):
    """
    Return a product only if it belongs to the logged-in seller.
    """

    return await get_product_by_id(
        db=db,

        seller_id=seller.id,

        product_id=product_id,
    )


# ============================================================
# DELETE PRODUCT
# ============================================================
#
# DELETE /api/v1/seller/products/{product_id}
#
# LOGIN REQUIRED
# ============================================================

@router.delete(
    "/{product_id}",
    status_code=204,
)
async def remove_product(
    product_id: int,

    db: AsyncSession = Depends(get_db),

    seller=Depends(get_current_seller),
):
    """
    Delete a product belonging to the logged-in seller.
    """

    await delete_product(
        db=db,

        seller_id=seller.id,

        product_id=product_id,
    )

    return None