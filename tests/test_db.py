import pytest

from trading_result_app.models.models import Base
from trading_result_app.database import async_engine
import trading_result_app.config as conf
from trading_result_app.config import Settings

conf.settings = Settings(_env_file=".test.env")


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    print(f"{conf.settings.DB_NAME}")
    Base.metadata.create_all(bind=async_engine)

# class DB_write:
    # async with async_session_maker() as session:
    #     item = Item(
    #         date=datetime.strptime('23-10-2024', '%d-%m-%Y').date(),
    #         exchange_product_id = 'A100UFM060G',
    #         exchange_product_name = 'Gasoline',
    #         delivery_basis_name = 'some base',
    #         oil_id = 'A100',
    #         delivery_basis_id = 'SBS',
    #         delivery_type_id='F',
    #         volume = 1555,
    #         count=200,
    #         total = 1555*200
    #     )
    #     session.add(item)
    #     await session.commit()
