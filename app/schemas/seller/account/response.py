from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SellerLocationResponse(BaseModel):

    latitude: Decimal | None

    longitude: Decimal | None

    google_place_id: str | None

    formatted_address: str | None


class StoreResponse(BaseModel):

    id: int

    store_name: str

    description: str | None

    store_phone: str | None

    address_line: str

    city: str

    district: str | None

    state: str

    country: str

    pincode: str

    latitude: Decimal

    longitude: Decimal

    google_place_id: str | None

    formatted_address: str | None

    is_active: bool


class SellerAccountCreateResponse(BaseModel):

    message: str

    seller_id: int

    account_id: int

    name: str

    email: str

    phone: str

    location: SellerLocationResponse

    store: StoreResponse

    created_at: datetime