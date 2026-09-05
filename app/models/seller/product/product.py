from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProductUnit(str, Enum):
    KG = "kg"
    LTR = "ltr"
    NOS = "nos"


class SellerProduct(Base):
    __tablename__ = "seller_products"

    # ==========================================================
    # PRIMARY KEY
    # ==========================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # ==========================================================
    # SELLER
    # ==========================================================

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("seller_auth.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # PRODUCT INFORMATION
    # ==========================================================

    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # ==========================================================
    # PRODUCT IMAGE
    # ==========================================================

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ==========================================================
    # QUANTITY
    # ==========================================================

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # ==========================================================
    # PRICE
    # ==========================================================

    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    # ==========================================================
    # LOCATION
    # ==========================================================

    location_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    latitude: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )

    longitude: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )

    # ==========================================================
    # AGRICULTURE / PRODUCT DATES
    # ==========================================================

    harvest_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    best_before_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # ==========================================================
    # STATUS
    # ==========================================================

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        index=True,
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )