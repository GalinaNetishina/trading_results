import datetime
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import ConfigDict, Field, field_validator

from models.models import Item


class ItemIdFilter(Filter):
    exchange_product_id: str | None = None
    delivery_basis_id: str | None = None
    delivery_type_id: str | None = None

    @field_validator("exchange_product_id", "delivery_basis_id", "delivery_type_id")
    def check_id(cls, value):
        return value.upper()

    class Constants(Filter.Constants):
        model = Item

    model_config = ConfigDict(exclude_none=True)


class ItemDateIdFilter(ItemIdFilter):
    date__gte: datetime.date | None = Field(
        alias="start_date",
        default=datetime.datetime.today().date() - datetime.timedelta(days=7),
    )
    date__lte: datetime.date | None = Field(
        alias="end_date", default=datetime.datetime.today().date()
    )

    model_config = {"extra": "allow"}
