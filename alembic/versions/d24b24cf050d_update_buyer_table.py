"""update buyer table

Revision ID: d24b24cf050d
Revises: 3e08a530f434
Create Date: 2026-09-05 16:03:44.715220

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d24b24cf050d"
down_revision: Union[str, Sequence[str], None] = "3e08a530f434"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ----------------------------------------------------------
    # 1. Add column temporarily allowing NULL
    # ----------------------------------------------------------

    op.add_column(
        "seller_products",
        sa.Column(
            "total_quantity",
            sa.Numeric(
                precision=14,
                scale=3,
            ),
            nullable=True,
        ),
    )

    # ----------------------------------------------------------
    # 2. Initialize existing rows
    #
    # For now each existing row gets its own quantity.
    # The application service will recalculate grouped
    # total_quantity when products are created/updated/stocked.
    # ----------------------------------------------------------

    op.execute(
        """
        UPDATE seller_products
        SET total_quantity = quantity
        WHERE total_quantity IS NULL
        """
    )

    # ----------------------------------------------------------
    # 3. Make the column NOT NULL
    # ----------------------------------------------------------

    op.alter_column(
        "seller_products",
        "total_quantity",
        existing_type=sa.Numeric(
            precision=14,
            scale=3,
        ),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "seller_products",
        "total_quantity",
    )