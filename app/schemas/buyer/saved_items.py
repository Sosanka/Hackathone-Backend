from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CartAddRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0)


class CartUpdateRequest(BaseModel):
    quantity: Decimal = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    product_id: int

    product_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

    quantity: Decimal
    unit: str
    price_per_unit: Decimal

    total_price: Decimal

    location_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SavedItemOut(BaseModel):
    id: int
    buyer_id: int
    product_id: int
    quantity: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SavedItemToggleResponse(BaseModel):
    message: str
    is_saved: bool
    saved_item: Optional[SavedItemOut] = None