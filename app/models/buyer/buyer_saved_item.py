from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.models.base import Base


class BuyerSavedItem(Base):

    __tablename__ = "buyer_saved_items"

    __table_args__ = (
        UniqueConstraint(
            "buyer_id",
            "product_id",
            name="uq_buyer_product_saved",
        ),
    )

    # ==========================================
    # ID
    # ==========================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # ==========================================
    # BUYER
    # ==========================================

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "buyer-auth.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==========================================
    # PRODUCT
    # ==========================================

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "seller_products.id",
            ondelete="CASCADE",
        ),
        nullable=False,
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