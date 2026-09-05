from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductResponseSchema(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    seller_id: int

    product_name: str

    description: str | None

    category: str | None

    image_url: str | None

    # Quantity for this particular entry
    quantity: Decimal

    # Total quantity of the same product
    total_quantity: Decimal

    unit: str

    price_per_unit: Decimal

    total_price: Decimal

    location_name: str | None

    address: str | None

    latitude: Decimal | None

    longitude: Decimal | None

    harvest_date: date | None

    best_before_date: date | None

    status: str

    created_at: datetime

    updated_at: datetime