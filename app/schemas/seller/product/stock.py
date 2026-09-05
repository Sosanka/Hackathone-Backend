from decimal import Decimal

from pydantic import BaseModel, Field


class StockAdjustmentSchema(BaseModel):

    quantity: Decimal = Field(
        ...,
        gt=0,
    )