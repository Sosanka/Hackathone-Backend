from decimal import Decimal

from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seller.product.product import SellerProduct

from app.schemas.seller.product.request import (
    ProductCreateSchema,
)

from app.schemas.seller.product.update import (
    ProductUpdateSchema,
)

from app.schemas.seller.product.stock import (
    StockAdjustmentSchema,
)

from app.services.seller.product.image import (
    delete_product_image,
    save_product_image,
)


# ============================================================
# CALCULATE TOTAL QUANTITY
# ============================================================

async def calculate_total_quantity(
    db: AsyncSession,
    seller_id: int,
    product_name: str,
    unit: str,
) -> Decimal:

    result = await db.execute(
        select(
            func.coalesce(
                func.sum(SellerProduct.quantity),
                0,
            )
        )
        .where(
            SellerProduct.seller_id == seller_id,

            func.lower(
                SellerProduct.product_name
            ) == product_name.lower(),

            SellerProduct.unit == unit,

            SellerProduct.status == "active",
        )
    )

    total = result.scalar()

    return Decimal(str(total or 0))


# ============================================================
# UPDATE TOTAL QUANTITY FOR SAME PRODUCT
# ============================================================

async def update_product_totals(
    db: AsyncSession,
    seller_id: int,
    product_name: str,
    unit: str,
) -> Decimal:

    total_quantity = await calculate_total_quantity(
        db=db,
        seller_id=seller_id,
        product_name=product_name,
        unit=unit,
    )

    result = await db.execute(
        select(SellerProduct)
        .where(
            SellerProduct.seller_id == seller_id,

            func.lower(
                SellerProduct.product_name
            ) == product_name.lower(),

            SellerProduct.unit == unit,

            SellerProduct.status == "active",
        )
    )

    products = result.scalars().all()

    for product in products:

        # ----------------------------------------------------
        # Update group total quantity
        # ----------------------------------------------------

        product.total_quantity = total_quantity

        # ----------------------------------------------------
        # Keep total_price for THIS entry
        # ----------------------------------------------------
        #
        # total_price = this row's quantity
        #               × this row's price
        #
        # Do NOT use total_quantity here.
        # ----------------------------------------------------

        product.total_price = (
            product.quantity
            * product.price_per_unit
        )

    return total_quantity


# ============================================================
# CREATE PRODUCT / ADD NEW STOCK ENTRY
# ============================================================

async def create_product(
    db: AsyncSession,
    seller_id: int,
    data: ProductCreateSchema,
    image: UploadFile | None = None,
) -> SellerProduct:

    image_url = None

    # --------------------------------------------------------
    # SAVE IMAGE
    # --------------------------------------------------------

    if image:
        image_url = await save_product_image(image)

    # --------------------------------------------------------
    # CREATE PRODUCT ENTRY
    # --------------------------------------------------------

    product = SellerProduct(
        seller_id=seller_id,

        product_name=data.product_name,

        description=data.description,

        category=data.category,

        image_url=image_url,

        # Quantity for this entry
        quantity=data.quantity,

        # Initially only this entry exists
        total_quantity=data.quantity,

        unit=data.unit,

        price_per_unit=data.price_per_unit,

        # Price for this entry
        total_price=(
            data.quantity
            * data.price_per_unit
        ),

        location_name=data.location_name,

        address=data.address,

        latitude=data.latitude,

        longitude=data.longitude,

        harvest_date=data.harvest_date,

        best_before_date=data.best_before_date,

        status="active",
    )

    db.add(product)

    try:

        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        await db.flush()

        # ----------------------------------------------------
        # RECALCULATE SAME PRODUCT TOTAL
        # ----------------------------------------------------

        await update_product_totals(
            db=db,
            seller_id=seller_id,
            product_name=data.product_name,
            unit=data.unit,
        )

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        await db.commit()

        await db.refresh(product)

    except Exception:

        await db.rollback()

        if image_url:
            delete_product_image(image_url)

        raise

    return product


# ============================================================
# GET ALL PRODUCTS
# ============================================================

async def get_seller_products(
    db: AsyncSession,
    seller_id: int,
) -> list[SellerProduct]:

    result = await db.execute(
        select(SellerProduct)
        .where(
            SellerProduct.seller_id == seller_id
        )
        .order_by(
            SellerProduct.created_at.desc()
        )
    )

    return list(
        result.scalars().all()
    )


# ============================================================
# GET PRODUCT BY ID
# ============================================================

async def get_product_by_id(
    db: AsyncSession,
    seller_id: int,
    product_id: int,
) -> SellerProduct:

    result = await db.execute(
        select(SellerProduct)
        .where(
            SellerProduct.id == product_id,

            SellerProduct.seller_id == seller_id,
        )
    )

    product = result.scalar_one_or_none()

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


# ============================================================
# UPDATE PRODUCT / STOCK ENTRY
# ============================================================

async def update_product(
    db: AsyncSession,
    seller_id: int,
    product_id: int,
    data: ProductUpdateSchema,
) -> SellerProduct:

    # --------------------------------------------------------
    # GET PRODUCT
    # --------------------------------------------------------

    product = await get_product_by_id(
        db=db,
        seller_id=seller_id,
        product_id=product_id,
    )

    # --------------------------------------------------------
    # SAVE OLD GROUP
    # --------------------------------------------------------

    old_product_name = product.product_name
    old_unit = product.unit

    # --------------------------------------------------------
    # UPDATE PROVIDED FIELDS ONLY
    # --------------------------------------------------------

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            product,
            field,
            value,
        )

    # --------------------------------------------------------
    # RECALCULATE THIS ENTRY PRICE
    # --------------------------------------------------------

    product.total_price = (
        product.quantity
        * product.price_per_unit
    )

    # --------------------------------------------------------
    # FLUSH
    # --------------------------------------------------------

    await db.flush()

    # --------------------------------------------------------
    # RECALCULATE OLD GROUP
    # --------------------------------------------------------

    await update_product_totals(
        db=db,
        seller_id=seller_id,
        product_name=old_product_name,
        unit=old_unit,
    )

    # --------------------------------------------------------
    # RECALCULATE NEW GROUP
    # --------------------------------------------------------

    await update_product_totals(
        db=db,
        seller_id=seller_id,
        product_name=product.product_name,
        unit=product.unit,
    )

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    await db.commit()

    await db.refresh(product)

    return product


# ============================================================
# ADD STOCK
# ============================================================

async def add_stock(
    db: AsyncSession,
    seller_id: int,
    product_id: int,
    data: StockAdjustmentSchema,
) -> SellerProduct:

    # --------------------------------------------------------
    # GET PRODUCT
    # --------------------------------------------------------

    product = await get_product_by_id(
        db=db,
        seller_id=seller_id,
        product_id=product_id,
    )

    # --------------------------------------------------------
    # ADD QUANTITY
    # --------------------------------------------------------

    product.quantity += data.quantity

    # --------------------------------------------------------
    # ACTIVATE PRODUCT
    # --------------------------------------------------------

    product.status = "active"

    # --------------------------------------------------------
    # UPDATE ENTRY PRICE
    # --------------------------------------------------------

    product.total_price = (
        product.quantity
        * product.price_per_unit
    )

    # --------------------------------------------------------
    # FLUSH
    # --------------------------------------------------------

    await db.flush()

    # --------------------------------------------------------
    # RECALCULATE TOTAL
    # --------------------------------------------------------

    await update_product_totals(
        db=db,
        seller_id=seller_id,
        product_name=product.product_name,
        unit=product.unit,
    )

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    await db.commit()

    await db.refresh(product)

    return product


# ============================================================
# SUBTRACT STOCK
# ============================================================

async def subtract_stock(
    db: AsyncSession,
    seller_id: int,
    product_id: int,
    data: StockAdjustmentSchema,
) -> SellerProduct:

    # --------------------------------------------------------
    # GET PRODUCT
    # --------------------------------------------------------

    product = await get_product_by_id(
        db=db,
        seller_id=seller_id,
        product_id=product_id,
    )

    # --------------------------------------------------------
    # CHECK AVAILABLE STOCK
    # --------------------------------------------------------

    if data.quantity > product.quantity:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot subtract {data.quantity} "
                f"{product.unit}. "
                f"Available stock is "
                f"{product.quantity} "
                f"{product.unit}."
            ),
        )

    # --------------------------------------------------------
    # SUBTRACT QUANTITY
    # --------------------------------------------------------

    product.quantity -= data.quantity

    # --------------------------------------------------------
    # UPDATE ENTRY PRICE
    # --------------------------------------------------------

    product.total_price = (
        product.quantity
        * product.price_per_unit
    )

    # --------------------------------------------------------
    # ZERO STOCK
    # --------------------------------------------------------

    if product.quantity == 0:

        product.status = "out_of_stock"

    # --------------------------------------------------------
    # FLUSH
    # --------------------------------------------------------

    await db.flush()

    # --------------------------------------------------------
    # RECALCULATE TOTAL
    # --------------------------------------------------------

    await update_product_totals(
        db=db,
        seller_id=seller_id,
        product_name=product.product_name,
        unit=product.unit,
    )

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    await db.commit()

    await db.refresh(product)

    return product


# ============================================================
# DELETE PRODUCT / STOCK ENTRY
# ============================================================

async def delete_product(
    db: AsyncSession,
    seller_id: int,
    product_id: int,
) -> None:

    # --------------------------------------------------------
    # GET PRODUCT
    # --------------------------------------------------------

    product = await get_product_by_id(
        db=db,
        seller_id=seller_id,
        product_id=product_id,
    )

    # --------------------------------------------------------
    # SAVE GROUP INFORMATION
    # --------------------------------------------------------

    product_name = product.product_name

    unit = product.unit

    image_url = product.image_url

    # --------------------------------------------------------
    # DELETE ENTRY
    # --------------------------------------------------------

    await db.delete(product)

    await db.flush()

    # --------------------------------------------------------
    # RECALCULATE REMAINING STOCK
    # --------------------------------------------------------

    await update_product_totals(
        db=db,
        seller_id=seller_id,
        product_name=product_name,
        unit=unit,
    )

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    await db.commit()

    # --------------------------------------------------------
    # DELETE IMAGE FROM CLOUDINARY
    # --------------------------------------------------------

    if image_url:

        delete_product_image(image_url)