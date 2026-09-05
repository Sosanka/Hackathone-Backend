from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ProductCreateSchema(BaseModel):

    product_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    # Quantity for this particular entry
    quantity: Decimal = Field(
        ...,
        gt=0,
    )

    unit: str = Field(
        ...,
        description="kg, ltr or nos",
    )

    price_per_unit: Decimal = Field(
        ...,
        gt=0,
    )

    location_name: str | None = Field(
        default=None,
        max_length=255,
    )

    address: str | None = None

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

    harvest_date: date | None = None

    best_before_date: date | None = None

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, value: str) -> str:

        value = value.lower().strip()

        allowed_units = {
            "kg",
            "ltr",
            "nos",
        }

        if value not in allowed_units:
            raise ValueError(
                "Unit must be one of: kg, ltr, nos"
            )

        return value

    @field_validator("product_name")
    @classmethod
    def clean_product_name(cls, value: str) -> str:
        return value.strip()