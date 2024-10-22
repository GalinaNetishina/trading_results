import datetime

from pydantic import BaseModel, Field
from fastapi_filter.contrib.sqlalchemy import Filter

from models import Item


class TradingDay(BaseModel):
    date: datetime.date


class ItemDTO(TradingDay, BaseModel):
    exchange_product_id: str
    exchange_product_name: str
    delivery_basis_name: str
    volume: int = Field(gt=0)
    total: int = Field(gt=0)
    count: int = Field(gt=0)


class ItemFull(ItemDTO):
    oil_id: str
    delivery_basis_id: str
    delivery_type_id: str


class ItemIdFilter(Filter):
    exchange_product_id: str | None = None
    delivery_basis_id: str | None = None
    delivery_type_id: str | None = None

    class Constants(Filter.Constants):
        model = Item


class ItemDateIdFilter(ItemIdFilter):
    model_config = {"extra": "allow"}
    date__gte: datetime.date | None = Field(
        alias="start_date",
        default=datetime.datetime.today().date() - datetime.timedelta(days=7),
    )
    date__lte: datetime.date | None = Field(
        alias="end_date", default=datetime.datetime.today().date()
    )
