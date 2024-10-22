import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator
from fastapi_filter.contrib.sqlalchemy import Filter

from models import Item


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


class ItemIdFilter(Filter):
    exchange_product_id: str | None = None
    delivery_basis_id: str | None = None
    delivery_type_id: str | None = None

    @field_validator('exchange_product_id', 'delivery_basis_id', 'delivery_type_id')
    def check_id(cls, value):
        return value.upper()    

    class Constants(Filter.Constants):
        model = Item


class ItemDateIdFilter(ItemIdFilter):
    date__gte: datetime.date | None = Field(
        alias="start_date",
        default=datetime.datetime.today().date() - datetime.timedelta(days=7),
    )
    date__lte: datetime.date | None = Field(
        alias="end_date", default=datetime.datetime.today().date()
    )

    model_config = {"extra": "allow"}