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
    ProductUpdateSchema,
)

from app.schemas.seller.product.response import (
    ProductResponseSchema,
)

from app.schemas.seller.product.stock import (
    StockAdjustmentSchema,
)

from app.services.seller.product.product import (
    add_stock,
    create_product,
    delete_product,
    get_product_by_id,
    get_seller_products,
    subtract_stock,
    update_product,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/products",
    tags=["Seller Products"],
)


# ============================================================
# CREATE PRODUCT / ADD NEW STOCK ENTRY
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

    seller=Depends(get_current_seller),
):
    """
    Create a new product/stock entry.

    total_quantity is calculated automatically
    by the backend.
    """

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

    return await create_product(
        db=db,
        seller_id=seller.id,
        data=data,
        image=image,
    )


# ============================================================
# GET ALL PRODUCTS
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
    Return all product/stock entries belonging
    to the logged-in seller.
    """

    return await get_seller_products(
        db=db,
        seller_id=seller.id,
    )


# ============================================================
# GET SINGLE PRODUCT / STOCK ENTRY
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
    Return a single product/stock entry.
    """

    return await get_product_by_id(
        db=db,
        seller_id=seller.id,
        product_id=product_id,
    )


# ============================================================
# UPDATE PRODUCT / STOCK ENTRY
# ============================================================

@router.put(
    "/{product_id}",
    response_model=ProductResponseSchema,
)
async def edit_product(
    product_id: int,
    data: ProductUpdateSchema,
    db: AsyncSession = Depends(get_db),
    seller=Depends(get_current_seller),
):
    """
    Update a product/stock entry.

    If quantity, product name, or unit changes,
    total_quantity is recalculated automatically.
    """

    return await update_product(
        db=db,
        seller_id=seller.id,
        product_id=product_id,
        data=data,
    )


# ============================================================
# ADD STOCK
# ============================================================

@router.post(
    "/{product_id}/stock/add",
    response_model=ProductResponseSchema,
)
async def increase_stock(
    product_id: int,
    data: StockAdjustmentSchema,
    db: AsyncSession = Depends(get_db),
    seller=Depends(get_current_seller),
):
    """
    Add stock to this specific stock entry.
    """

    return await add_stock(
        db=db,
        seller_id=seller.id,
        product_id=product_id,
        data=data,
    )


# ============================================================
# SUBTRACT STOCK
# ============================================================

@router.post(
    "/{product_id}/stock/subtract",
    response_model=ProductResponseSchema,
)
async def decrease_stock(
    product_id: int,
    data: StockAdjustmentSchema,
    db: AsyncSession = Depends(get_db),
    seller=Depends(get_current_seller),
):
    """
    Subtract stock from this specific stock entry.

    Stock cannot become negative.
    """

    return await subtract_stock(
        db=db,
        seller_id=seller.id,
        product_id=product_id,
        data=data,
    )


# ============================================================
# DELETE PRODUCT / STOCK ENTRY
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
    Delete a product/stock entry.

    After deletion, total_quantity for the
    remaining matching entries is recalculated.
    """

    await delete_product(
        db=db,
        seller_id=seller.id,
        product_id=product_id,
    )

    return None