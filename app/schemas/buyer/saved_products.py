from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SavedProductCreateSchema(BaseModel):
    product_id: int


class SavedProductProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_name: str
    description: str | None = None
    category: str | None = None
    image_url: str | None = None
    quantity: Decimal | None = None
    unit: str | None = None
    price_per_unit: Decimal | None = None
    location_name: str | None = None
    status: str | None = None


class SavedProductResponseSchema(BaseModel):
    id: int
    product_id: int
    created_at: datetime
    product: SavedProductProductSchema

    model_config = ConfigDict(from_attributes=True)


class SavedProductToggleResponseSchema(BaseModel):
    product_id: int
    saved: bool
    message: str