from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BuyerOrder(Base):

    __tablename__ = "buyer_orders"

    # ==========================================================
    # PRIMARY KEY
    # ==========================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # ==========================================================
    # BUYER
    # ==========================================================

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "buyer-auth.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # PRODUCT
    # ==========================================================

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "seller_products.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # SELLER
    # ==========================================================

    seller_id: Mapped[int] = mapped_column(
        ForeignKey(
            "seller_auth.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # ==========================================================
    # PRODUCT SNAPSHOT
    # ==========================================================

    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    # ==========================================================
    # CUSTOMER INFORMATION
    # ==========================================================

    customer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    customer_phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # ==========================================================
    # DELIVERY LOCATION
    # ==========================================================

    location_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    delivery_address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
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
    # ORDER STATUS
    # ==========================================================

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="placed",
        server_default="placed",
        index=True,
    )

    # ==========================================================
    # TIMESTAMP
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