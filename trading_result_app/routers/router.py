from typing import Annotated
from fastapi import BackgroundTasks
from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.schema import ItemFull, TradingDay
from schemas.filters import ItemDateIdFilter, ItemIdFilter
from database import get_async_session
from services.service import ItemService, DaysService, LoadService


router = APIRouter(prefix="/api")


def get_pag_params(limit: int = 10, skip: int = 0):
    return {"limit": limit, "skip": skip}


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@cache(expire=3600)
@router.get(
    "/get_trading_results/",
    tags=["Список последних торгов"],
    status_code=status.HTTP_200_OK,
)
async def get_trading_results(
    session: SessionDep,
    pag_params=Depends(get_pag_params),
    filter: ItemIdFilter = FilterDepends(ItemIdFilter),
) -> list[ItemFull]:
    service = ItemService(session)
    res = await service.get_items(filter, **pag_params)
    return res


@cache(expire=3600)
@router.get(
    "/get_dynamics/",
    tags=["Список торгов  в диапазоне дат"],
    status_code=status.HTTP_200_OK,
)
async def get_dynamics(
    session: SessionDep,
    pag_params=Depends(get_pag_params),
    filter: ItemIdFilter = FilterDepends(ItemDateIdFilter),
) -> list[ItemFull]:
    service = ItemService(session)
    res = await service.get_dynamic(filter, **pag_params)
    return res


@cache(expire=3600)
@router.get("/item/{id}", tags=["Детали о лоте по id"], status_code=status.HTTP_200_OK)
async def get_item(id: int, session: SessionDep) -> ItemFull:
    service = ItemService(session)
    res = await service.get_item_by_id(id)
    return res


@cache(expire=3600)
@router.get(
    "/last_trading_dates/",
    tags=["Даты последних торгов"],
    status_code=status.HTTP_200_OK,
)
async def get_last_trading_dates(
    session: SessionDep, count: int = 7
) -> list[TradingDay]:
    service = DaysService(session)
    res = await service.get_days(count)
    return res


@cache(expire=3600)
@router.get(
    "/last_trading_date/",
    tags=["Дата последнего торга"],
    status_code=status.HTTP_200_OK,
)
async def get_last_trading_day(session: SessionDep) -> TradingDay:
    service = DaysService(session)
    res = await service.get_day()
    return res


@router.get("/clear_cash/")
async def clear():
    from main import app

    await app.state.redis.flushdb()
    return {"message": "cache cleared"}


@router.get("/DB_load/")
async def db_load(tasks: BackgroundTasks, session: SessionDep):
    service = LoadService(session)
    if await service.is_loading_needed:
        tasks.add_task(service.load)
        return {"message": "loading started"}
    else:
        return {"message": "loading not needed"}
