from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SellerStore(Base):

    __tablename__ = "seller-stores"

    # ==========================================
    # ID
    # ==========================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # ==========================================
    # SELLER
    # ==========================================

    seller_id: Mapped[int] = mapped_column(
        ForeignKey(
            "seller-auth.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==========================================
    # STORE INFORMATION
    # ==========================================

    store_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    store_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # ==========================================
    # STORE ADDRESS
    # ==========================================

    address_line: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="India",
        server_default="India",
        index=True,
    )

    pincode: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    # ==========================================
    # STORE GPS
    # ==========================================

    latitude: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=10,
            scale=7,
        ),
        nullable=False,
        index=True,
    )

    longitude: Mapped[Decimal] = mapped_column(
        Numeric(
            precision=10,
            scale=7,
        ),
        nullable=False,
        index=True,
    )

    # ==========================================
    # GOOGLE MAPS
    # ==========================================

    google_place_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    formatted_address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ==========================================
    # ACTIVE
    # ==========================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    # ==========================================
    # CREATED
    # ==========================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ==========================================
    # UPDATED
    # ==========================================

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )