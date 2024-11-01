from httpx import AsyncClient
import pytest
from trading_result_app.schemas.schema import ItemFull, TradingDay


class TestApiTradingResultsBase:
    async def test_get_last_results(self, ac: AsyncClient):
        response = await ac.get("/api/get_trading_results/")
        assert response.status_code == 200, f"{response.json()}"
        for item in response.json():
            ItemFull.model_validate(item)

        last_date = await ac.get("/api/last_trading_date/")
        TradingDay.model_validate(last_date.json())
        assert response.json()[0]["date"] == last_date.json()["date"]


class TestApiTradingResultsPagination:
    async def test_get_last_results_with_pagination(self, ac: AsyncClient):
        response = await ac.get("/api/get_trading_results/?limit=5")
        assert response.status_code == 200, f"{response.json()}"
        assert len(response.json()) == 5
        first5 = response.json()

        response = await ac.get("/api/get_trading_results/?limit=5&skip=5")
        assert response.status_code == 200, f"{response.json()}"
        assert len(response.json()) == 5
        second5 = response.json()
        response = await ac.get("/api/get_trading_results/")
        for item in first5 + second5:
            assert item in response.json()


class TestApiTradingResultsFilters:
    @pytest.mark.parametrize(
        "filter_name, values",
        [
            ("delivery_basis_id", "basis_ids"),
            ("exchange_product_id", "product_ids"),
            ("delivery_type_id", "types_ids"),
        ],
    )
    @pytest.mark.usefixtures("generate_dict_lists_ids")
    async def test_id_filter(self, ac: AsyncClient, filter_name, values):
        for value, func in zip(
            self.ids[values], [str.lower, str.upper, str.capitalize]
        ):
            response = await ac.get(
                f"/api/get_trading_results/?{filter_name}={func(value)}&limit=3"
            )
            assert response.status_code == 200, f"{response.json()}"
            for item in response.json():
                assert item[filter_name] == value


class TestApiResultsOrdering:
    async def test_last_result_ordering(self, ac: AsyncClient):
        limit = 100
        skip = 0
        retrieved_dates = []
        for _ in range(5):
            url = f"api/get_trading_results/?limit={limit}&skip={skip}"
            response = await ac.get(url)
            if not response.json():
                break
            for item in response.json():
                day = item["date"]
                if day not in retrieved_dates:
                    retrieved_dates.append(day)
            skip += limit
        assert retrieved_dates == sorted(
            retrieved_dates, reverse=True
        ), "check ordering"
