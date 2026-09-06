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
    relationship,
)

from app.models.base import Base


class BuyerSavedProduct(Base):

    __tablename__ = "buyer_saved_products"

    # ==========================================
    # ID
    # ==========================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # ==========================================
    # BUYER ID
    # ==========================================

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("buyer-auth.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ==========================================
    # PRODUCT ID
    # ==========================================

    product_id: Mapped[int] = mapped_column(
        ForeignKey("seller_products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ==========================================
    # CREATED AT
    # ==========================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ==========================================
    # RELATIONSHIPS
    # ==========================================

    buyer = relationship(
        "Buyer",
        back_populates="saved_products",
    )

    product = relationship(
        "SellerProduct",
    )

    # ==========================================
    # CONSTRAINTS
    # ==========================================

    __table_args__ = (
        UniqueConstraint(
            "buyer_id",
            "product_id",
            name="uq_buyer_saved_product",
        ),
    )