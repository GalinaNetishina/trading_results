from sqlalchemy import desc, select
from sqlalchemy.orm import load_only
from redis import asyncio as aioredis
from models.models import Item

from schemas.schema import TradingDay
from config import settings
from repos.sqlalchemy_repo import SQLAlchemyWriteRepo, SQLAlchemyReadRepo


redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf8",
    decode_responses=True,
)


class WriteItemRepo(SQLAlchemyWriteRepo):
    model = Item


class ReadItemRepo(SQLAlchemyReadRepo):
    model = Item

    async def get_dynamic(self, filter, limit, skip, order_by):
        async with self.session as session:
            query = select(self.model).order_by(order_by)
            query = (
                filter.filter(query)
                .where(Item.date.between(filter.date__gte, filter.date__lte))
                .limit(limit)
                .offset(skip)
            )
            res = await session.execute(query)
            return res.scalars().all()


class ReadDaysRepo(SQLAlchemyReadRepo):
    model = Item

    async def get_many(self, count: int) -> list[TradingDay]:
        query = (
            select(Item)
            .order_by(desc(Item.date))
            .options(load_only(Item.date))
            .distinct(Item.date)
            .limit(count)
        )
        res = await self.session.execute(query)
        return list(
            map(
                lambda x: TradingDay.model_validate(x, from_attributes=True),
                res.scalars().all(),
            )
        )

    async def get_one(self) -> TradingDay:
        query = (
            select(Item)
            .order_by(desc(Item.date))
            .options(load_only(Item.date))
            .distinct(Item.date)
            .limit(1)
        )
        res = await self.session.execute(query)
        res_dto = TradingDay.model_validate(
            res.scalars().one_or_none(), from_attributes=True
        )
        return res_dto
