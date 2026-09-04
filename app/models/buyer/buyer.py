from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.models.base import Base


class Buyer(Base):

    __tablename__ = "buyer-auth"

    # ==========================================
    # ID
    # ==========================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # ==========================================
    # NAME
    # ==========================================

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    # ==========================================
    # EMAIL
    # ==========================================

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    # ==========================================
    # PHONE
    # ==========================================

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    # ==========================================
    # PASSWORD
    # ==========================================

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ==========================================
    # EMAIL VERIFIED
    # ==========================================

    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )

    # ==========================================
    # ACCOUNT ACTIVE
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