from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class SellerAccountCreateRequest(BaseModel):

    # ==================================================
    # SELLER PROFILE
    # ==================================================

    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    address_line: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    district: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    country: str = Field(
        default="India",
        max_length=100,
    )

    pincode: str | None = Field(
        default=None,
        max_length=10,
    )

    # ==================================================
    # SELLER GPS
    # ==================================================

    latitude: Decimal | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: Decimal | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    google_place_id: str | None = Field(
        default=None,
        max_length=255,
    )

    formatted_address: str | None = Field(
        default=None,
        max_length=500,
    )

    # ==================================================
    # STORE
    # ==================================================

    store_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    store_description: str | None = Field(
        default=None,
        max_length=2000,
    )

    store_phone: str | None = Field(
        default=None,
        max_length=20,
    )

    store_address_line: str = Field(
        ...,
        min_length=3,
        max_length=255,
    )

    store_city: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    store_district: str | None = Field(
        default=None,
        max_length=100,
    )

    store_state: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    store_country: str = Field(
        default="India",
        max_length=100,
    )

    store_pincode: str = Field(
        ...,
        min_length=4,
        max_length=10,
    )

    # ==================================================
    # STORE GPS
    # ==================================================

    store_latitude: Decimal = Field(
        ...,
        ge=-90,
        le=90,
    )

    store_longitude: Decimal = Field(
        ...,
        ge=-180,
        le=180,
    )

    store_google_place_id: str | None = Field(
        default=None,
        max_length=255,
    )

    store_formatted_address: str | None = Field(
        default=None,
        max_length=500,
    )

    # ==================================================
    # VALIDATORS
    # ==================================================

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError(
                "Name cannot be empty."
            )

        return value

    @field_validator("store_name")
    @classmethod
    def validate_store_name(cls, value: str):

        value = value.strip()

        if not value:
            raise ValueError(
                "Store name cannot be empty."
            )

        return value

    @field_validator(
        "pincode",
        "store_pincode",
    )
    @classmethod
    def validate_pincode(
        cls,
        value: str | None,
    ):

        if value is None:
            return None

        value = value.strip()

        if not value.isdigit():
            raise ValueError(
                "Pincode must contain only numbers."
            )

        return value