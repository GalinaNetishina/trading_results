from datetime import date
import pytest


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


@pytest.fixture(scope="module", autouse=True)
async def load_data():
    async with async_session_maker() as session:           
        serv = LoadService(session)
        await serv.load()

class TestWriteRepo:
    async def test_days_service(self):
        async with async_session_maker() as session:           
            serv = DaysService(session)
            days = await serv.get_days(count=5)
            for day in days:
                assert type(day.date) == date
    
    async def test_item_service(self):
        async with async_session_maker() as session:           
            serv = ItemService(session)
            filter = ItemIdFilter()
            items = await serv.get_items(filter, limit=5, skip=0)
            for item in items:
                assert type(item.date) == date
                assert type(item.delivery_basis_name) == str
                assert type(item.delivery_type_id) == str
                assert type(item.delivery_basis_id) == str
                assert type(item.exchange_product_name) == str
                assert type(item.exchange_product_id    ) == str
                assert type(item.count) == int
                assert type(item.total) == int
                assert type(item.volume) == int
           
    
        

