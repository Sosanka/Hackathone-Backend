from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SellerAccount(Base):

    __tablename__ = "seller_accounts"

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
            "seller_auth.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # ==========================================
    # PERSONAL INFORMATION
    # ==========================================

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    # ==========================================
    # ADDRESS
    # ==========================================

    address_line: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="India",
        server_default="India",
        index=True,
    )

    pincode: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
    )

    # ==========================================
    # SELLER LOCATION
    # ==========================================

    latitude: Mapped[Decimal | None] = mapped_column(
        Numeric(
            precision=10,
            scale=7,
        ),
        nullable=True,
        index=True,
    )

    longitude: Mapped[Decimal | None] = mapped_column(
        Numeric(
            precision=10,
            scale=7,
        ),
        nullable=True,
        index=True,
    )

    # ==========================================
    # GOOGLE PLACE
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