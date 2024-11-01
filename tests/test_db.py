from datetime import date
import datetime
import json


import trading_result_app.config as conf
from trading_result_app.config import Settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


from trading_result_app.config import settings
from trading_result_app.schemas.filters import ItemIdFilter
from trading_result_app.services.service import LoadService, DaysService, ItemService

DATABASE_URL = settings.TEST_DB_URL
engine_test = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)
conf.settings = Settings(_env_file=".test.env")


class TestReadRepo:
    async def test_load_data(self, monkeypatch):
        async def alternative_load(self):
            with open("test_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                await self.repo.add_one(
                    {
                        "exchange_product_id": item["exchange_product_id"],
                        "exchange_product_name": item["exchange_product_name"],
                        "oil_id": item["oil_id"],
                        "delivery_basis_id": item["delivery_basis_id"],
                        "delivery_basis_name": item["delivery_basis_name"],
                        "delivery_type_id": item["delivery_type_id"],
                        "volume": item["volume"],
                        "total": item["total"],
                        "count": item["count"],
                        "date": datetime.datetime.strptime(
                            item["date"], "%Y-%m-%d"
                        ).date(),
                    }
                )

        monkeypatch.setattr(
            "trading_result_app.services.service.LoadService.load", alternative_load
        )
        async with async_session_maker() as session:
            serv = LoadService(session)
            await serv.load()

    async def test_days_service(self):
        async with async_session_maker() as session:
            serv = DaysService(session)
            days = await serv.get_days(count=5)
            for day in days:
                assert type(day.date) is date

    async def test_item_service(self):
        async with async_session_maker() as session:
            serv = ItemService(session)
            filter = ItemIdFilter()
            items = await serv.get_items(filter, limit=5, skip=0)
            for item in items:
                assert type(item.date) is date
                assert type(item.delivery_basis_name) is str
                assert type(item.delivery_type_id) is str
                assert type(item.delivery_basis_id) is str
                assert type(item.exchange_product_name) is str
                assert type(item.exchange_product_id) is str
                assert type(item.count) is int
                assert type(item.total) is int
                assert type(item.volume) is int
