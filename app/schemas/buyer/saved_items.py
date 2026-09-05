from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SavedItemToggleResponse(BaseModel):

    saved: bool

    product_id: int


class SavedItemOut(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    product_id: int

    created_at: datetime

    product_name: str

    price_per_unit: float

    unit: str

    image_url: Optional[str] = None

    seller_name: Optional[str] = None

    location_name: Optional[str] = None

    is_active: Optional[bool] = True