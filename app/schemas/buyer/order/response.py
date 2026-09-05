from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class StockCheckResponse(BaseModel):

    product_id: int

    requested_quantity: Decimal

    available_quantity: Decimal

    unit: str

    available: bool

    message: str


class OrderResponseSchema(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    buyer_id: int

    product_id: int

    seller_id: int

    product_name: str

    quantity: Decimal

    unit: str

    price_per_unit: Decimal

    total_price: Decimal

    customer_name: str

    customer_phone: str

    location_name: str | None

    delivery_address: str

    latitude: Decimal | None

    longitude: Decimal | None

    status: str

    created_at: datetime

    updated_at: datetime