import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class TradingDay(BaseModel):
    date: datetime.date


class ItemDTO(TradingDay, BaseModel):
    exchange_product_id: str
    exchange_product_name: str
    delivery_basis_name: str
    volume: Annotated[int, Field(gt=0)]
    total: Annotated[int, Field(gt=0)]
    count: Annotated[int, Field(gt=0)]


class ItemFull(ItemDTO):
    id: int
    oil_id: str
    delivery_basis_id: str
    delivery_type_id: str
