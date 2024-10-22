import logging
from sqlalchemy import desc, select
from sqlalchemy.orm import load_only
from redis import asyncio as aioredis
from models import Item

from schema import ItemFull, TradingDay
from config import settings


redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf8",
    decode_responses=True,
)


class WriteItemRepo:
    @classmethod
    async def add_one(cls, session, data: Item) -> int:
        item = data
        session.add(item)
        await session.flush()
        await session.commit()
        return item.id

    @classmethod
    async def add_many(cls, session, data) -> None:
        session.add_all(data)
        logging.debug("db_part")


# эксперимент
# class ReadItemRepoTest(SQLAlchemyReadRepo):
#     model = Item


class ReadItemRepo:
    @classmethod
    async def get_one(cls, session, id: int) -> ItemFull:
        item = await redis.get(f"item_{id}")
        if item:
            return ItemFull.model_validate_json(item)
        query = select(Item).filter_by(id=id)
        res = await session.execute(query)
        res_dto = ItemFull.model_validate(
            res.scalars().one_or_none(), from_attributes=True
        )
        await redis.set(f"item_{id}", res_dto.model_dump_json())
        return res_dto

    @classmethod
    async def get_last(cls, session, filter, limit, skip) -> list[ItemFull]:
        subq = (
            select(Item)
            .order_by(desc(Item.date))
            .options(load_only(Item.date))
            .distinct(Item.date)
            .limit(1)
        ).subquery()
        query = filter.filter(
            select(Item).where(Item.date == subq.c.date).limit(limit).offset(skip)
        )
        res = await session.execute(query)
        return list(
            map(
                lambda x: ItemFull.model_validate(x, from_attributes=True),
                res.scalars().all(),
            )
        )

    @classmethod
    async def get_many(cls, session, filter, limit, skip) -> list[ItemFull]:
        query = filter.filter(
            select(Item)
            .where(Item.date.between(filter.date__gte, filter.date__lte))
            .limit(limit)
            .offset(skip)
        )
        res = await session.execute(query)
        return list(
            map(
                lambda x: ItemFull.model_validate(x, from_attributes=True),
                res.scalars().all(),
            )
        )


class TradingDatesRepo:
    @classmethod
    async def get_many(cls, session, count: int) -> list[TradingDay]:
        query = (
            select(Item)
            .order_by(desc(Item.date))
            .options(load_only(Item.date))
            .distinct(Item.date)
            .limit(count)
        )
        res = await session.execute(query)
        return list(
            map(
                lambda x: TradingDay.model_validate(x, from_attributes=True),
                res.scalars().all(),
            )
        )

    # @classmethod
    # async def get_one(cls, session) -> TradingDay:
    #     query = (
    #         select(Item)
    #         .order_by(desc(Item.date))
    #         .options(load_only(Item.date))
    #         .distinct(Item.date)
    #         .limit(1)
    #     )
    #     res = await session.execute(query)
    #     res_dto = TradingDay.model_validate(
    #         res.scalars().one_or_none(), from_attributes=True
    #     )
    #     return res_dto
