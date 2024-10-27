from httpx import AsyncClient
import pytest
from trading_result_app.schemas.schema import ItemFull


class TestApiDynamicBase:
    async def test_get_dynamics(self, ac: AsyncClient):
        response = await ac.get("/api/get_dynamics/")
        assert response.status_code == 200, f"{response.json()}"
        ItemFull.model_validate(response.json()[0])

        last_date = await ac.get("/api/last_trading_date/")
        assert response.json()[0]["date"] <= last_date.json()["date"]


class TestApiDynamicPagination:
    async def test_get_last_results_with_pagination(self, ac: AsyncClient):
        response = await ac.get("/api/get_dynamics/?limit=5")
        assert response.status_code == 200, f"{response.json()}"
        assert len(response.json()) == 5
        first5 = response.json()

        response = await ac.get("/api/get_dynamics/?limit=5&skip=5")
        assert response.status_code == 200, f"{response.json()}"
        assert len(response.json()) == 5
        second5 = response.json()
        response = await ac.get("/api/get_dynamics/")
        for item in first5 + second5:
            ItemFull.model_validate(item)
            assert item in response.json()


class TestApiDynamicFilters:
    @pytest.fixture
    async def generate_dict_ids(self, ac: AsyncClient, request):
        examples = await ac.get("/api/get_trading_results/?limit=1")
        request.cls.ids = dict()
        request.cls.ids["basis_id"] = examples.json()[0]["delivery_basis_id"]
        request.cls.ids["type_id"] = examples.json()[0]["delivery_type_id"]
        request.cls.ids["product_id"] = examples.json()[0]["exchange_product_id"]
        
    @pytest.mark.parametrize(
        "filter_name, values",
        [
            ("delivery_basis_id", "basis_id"),
            ("exchange_product_id", "product_id"),
            ("delivery_type_id", "type_id"),
        ],
    )
    @pytest.mark.usefixtures("generate_dict_ids")
    async def test_id_filter(self, ac: AsyncClient, filter_name, values):
        ids = (
            self.ids[values],
            self.ids[values].upper(),
            self.ids[values].capitalize(),
        )
        for id in ids:
            response = await ac.get(f"/api/get_dynamics/?{filter_name}={id}&limit=3")
            assert response.status_code == 200, f"{response.json()}"
            for item in response.json():
                assert item[filter_name] == self.ids[values]

    async def test_date_filters(self, ac: AsyncClient):
        example = await ac.get("/api/last_trading_dates/?count=5")
        days = [i["date"] for i in example.json()]
        response = await ac.get(f"/api/get_dynamics/?start_date={days[2]}&limit=100")
        assert response.status_code == 200, f"{response.json()}"
        for item in response.json():
            assert item["date"] >= days[2], "check start_date filter"

        response = await ac.get(
            f"/api/get_dynamics/?start_date={days[2]}&end_date={days[2]}&limit=100&skip=100"
        )
        assert response.status_code == 200, f"{response.json()}"
        for item in response.json():
            assert item["date"] == days[2], "check concrete_date_filter"

        response = await ac.get(
            f"/api/get_dynamics/?end_date={days[2]}&limit=100&skip=100"
        )
        assert response.status_code == 200, f"{response.json()}"
        assert response.json()[0]["date"] in days, "default start date near week ago"
        for item in response.json():
            assert item["date"] <= days[2], "check end_date filter"


class TestApiDynamicOrder:
    async def test_dynamic_ordering(self, ac: AsyncClient):
        example = await ac.get("/api/last_trading_dates/?count=3")
        days = [i["date"] for i in example.json()]
        limit = 100
        skip = 0
        start = days[-1]
        end = days[0]
        retrieved_dates = []
        while True:
            url = f"api/get_dynamics/?start_date={start}&end_date={end}&limit={limit}&skip={skip}"
            response = await ac.get(url)
            if not response.json():
                break
            for item in response.json():
                day = item["date"]
                assert day in days
                if day not in retrieved_dates:
                    retrieved_dates.append(day)
            skip += limit
        assert retrieved_dates == sorted(retrieved_dates), "check ordering"
