from httpx import AsyncClient
import pytest


@pytest.fixture
async def generate_dict_lists_ids(request, ac: AsyncClient):
    examples = await ac.get("/api/get_trading_results/?limit=3")
    basis_ids = [i["delivery_basis_id"] for i in examples.json()]
    product_ids = [i["exchange_product_id"] for i in examples.json()]
    types_ids = [i["delivery_type_id"] for i in examples.json()]
    request.cls.ids = {
        "basis_ids": basis_ids,
        "types_ids": types_ids,
        "product_ids": product_ids,
    }

@pytest.fixture()
async def generate_dict_ids(ac: AsyncClient, request):
    examples = await ac.get("/api/get_trading_results/?limit=1")
    request.cls.ids = dict()
    request.cls.ids["basis_id"] = examples.json()[0]["delivery_basis_id"]
    request.cls.ids["type_id"] = examples.json()[0]["delivery_type_id"]
    request.cls.ids["product_id"] = examples.json()[0]["exchange_product_id"]