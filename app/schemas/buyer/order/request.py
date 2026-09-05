from decimal import Decimal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class StockCheckRequest(BaseModel):

    quantity: Decimal = Field(
        ...,
        gt=0,
    )


class OrderCreateSchema(BaseModel):

    # ==========================================================
    # PRODUCT
    # ==========================================================

    product_id: int = Field(
        ...,
        gt=0,
    )

    quantity: Decimal = Field(
        ...,
        gt=0,
    )

    # ==========================================================
    # CUSTOMER
    # ==========================================================

    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    customer_phone: str = Field(
        ...,
        min_length=7,
        max_length=30,
    )

    # ==========================================================
    # LOCATION
    # ==========================================================

    location_name: str | None = Field(
        default=None,
        max_length=255,
    )

    delivery_address: str = Field(
        ...,
        min_length=5,
        max_length=5000,
    )

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

    # ==========================================================
    # VALIDATORS
    # ==========================================================

    @field_validator("customer_name")
    @classmethod
    def clean_customer_name(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Customer name is required"
            )

        return value

    @field_validator("customer_phone")
    @classmethod
    def clean_customer_phone(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Customer phone is required"
            )

        return value

    @field_validator("delivery_address")
    @classmethod
    def clean_address(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Delivery address is required"
            )

        return value