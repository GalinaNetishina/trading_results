from httpx import AsyncClient
from trading_result_app.schemas.schema import ItemFull, TradingDay


class TestApiDates:
    async def test_get_dates(self, ac: AsyncClient):
        response = await ac.get("/api/last_trading_dates/")
        assert response.status_code == 200, f"{response.json()}"
        assert len(response.json()) <= 7
        response = await ac.get("/api/last_trading_date/")
        TradingDay.model_validate(response.json())
        assert 'date' in response.json() 

    async def test_get_dates_with_count(self, ac: AsyncClient):
        response = await ac.get("/api/last_trading_dates/?count=3")
        assert response.status_code == 200, f"{response.json()}"
        assert len(response.json()) == 3
        for day in response.json():
            TradingDay.model_validate(day)


class TestApiGetbyId:
    async def test_get_item_by_id(self, ac: AsyncClient):
        example = await ac.get("/api/get_trading_results/?limit=1")
        assert example.status_code == 200, f"{example.json()}"
        assert len(example.json()) == 1
        id = example.json()[0]["id"]

        response = await ac.get(f"/api/item/{id}")
        assert response.status_code == 200, f"{response.json()}"
        ItemFull.model_validate(response.json())
        assert response.json() == example.json()[0]

    async def test_get_item_by_unexisting_id(self, ac: AsyncClient):
        response = await ac.get("/api/item/99999999")
        assert response.status_code == 404, f"{response.json()}"
