from abc import ABC
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError


class AbstractRepository(ABC):
    model = None

    def __init__(self, session):
        self.session = session


class SQLAlchemyWriteRepo(AbstractRepository):
    async def add_one(self, data: dict):
        async with self.session as session:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            res = await session.execute(stmt)
            await session.commit()
            await session.flush()
            return res.scalar_one()

    async def add_many(self, data) -> None:
        async with self.session as session:
            try:
                session.add_all(data)
                await session.commit()
            except IntegrityError:
                await session.rollback()


class SQLAlchemyReadRepo(AbstractRepository):
    model = None

    async def get_one(self, id):
        async with self.session as session:
            query = select(self.model).where(self.model.id == id)
            res = await session.execute(query)
            return res.scalar_one_or_none()

    async def get_many(self, filters, limit, skip, order_by):
        async with self.session as session:
            query = select(self.model).order_by(order_by)
            query = filters.filter(query).limit(limit).offset(skip)
            res = await session.execute(query)
            return res.scalars().all()
