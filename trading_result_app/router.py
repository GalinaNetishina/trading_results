import logging
from fastapi import BackgroundTasks, HTTPException
from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from schema import ItemDTO, ItemFull, TradingDay, ItemDateIdFilter, ItemIdFilter
from database import get_async_session
import repository as r
from config import settings


router = APIRouter(prefix="/api")
redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf8",
    decode_responses=True,
)


def get_pag_params(limit: int = 10, skip: int = 0):
    return {"limit": limit, "skip": skip}


@cache(expire=3600)
@router.get("/get_trading_results/", tags=["Список последних торгов"])
async def get_trading_results(
    pag_params=Depends(get_pag_params),
    filter: ItemIdFilter = FilterDepends(ItemIdFilter),
    session: AsyncSession = Depends(get_async_session),
) -> list[ItemDTO]:
    res = await r.ReadItemRepo.get_last(session, filter, **pag_params)
    return res


@cache(expire=3600)
@router.get("/get_dynamics/", tags=["Список торгов  в диапазоне дат"])
async def get_dynamics(
    pag_params=Depends(get_pag_params),
    filter: ItemIdFilter = FilterDepends(ItemDateIdFilter),
    session: AsyncSession = Depends(get_async_session),
) -> list[ItemDTO]:
    res = await r.ReadItemRepo.get_many(session, filter, **pag_params)
    return res


# тест с наследованием репозиториев от SQLAlchemyReadRepo, работал
# @cache(expire=3600)
# @router.get("/test/{id}", tags=["Детали о лоте по id"])
# async def test_item(id :int,
# ) -> ItemFull:
#     res = await r.ReadItemRepoTest.get_one(id)
#     return res


@cache(expire=3600)
@router.get("/item/{id}", tags=["Детали о лоте по id"])
async def get_item(
    id: int, session: AsyncSession = Depends(get_async_session)
) -> ItemFull:
    try:
        res = await r.ReadItemRepo.get_one(session, id)
        return res
    except Exception:
        raise HTTPException(status_code=400, detail="Item not exists")


@cache(expire=3600)
@router.get("/last_trading_dates/", tags=["Даты последних торгов"])
async def get_last_trading_dates(
    session: AsyncSession = Depends(get_async_session), count: int = 10
) -> list[TradingDay]:
    res = await r.TradingDatesRepo.get_many(session, count)
    return res


@router.get("/clear_cash/")
async def clear():
    await redis.flushdb()
    return {"message": "cache cleared"}


@router.get("/DB_load/")
async def db_load(
    tasks: BackgroundTasks,
    ):
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    from functools import partial
    from datetime import datetime, timedelta
    from database import async_engine
    import repository as r
    from utils import Downloader

    session_maker = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    async with session_maker() as session:
        after = "01.10.2024"
        
        dates = await r.TradingDatesRepo.get_many(session, 1)
        if not dates:
            response = {"message": f"data after {after} loading"}
            dl = Downloader(after, partial(r.WriteItemRepo.add_many, session))
            tasks.add_task(dl.download)
        elif dates and (datetime.today().date() - dates[0].date > timedelta(days=3)):
                after = dates[0].date.strftime("%d.%m.%Y")
                response = {"message": f"data after {after} loading"}
                dl = Downloader(after, partial(r.WriteItemRepo.add_many, session))
                tasks.add_task(dl.download)
        else:
            response = {"message": f'data still fresh, last trading date = {dates[0].date.strftime("%d.%m.%Y")}'}
        return response
