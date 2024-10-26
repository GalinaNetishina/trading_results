from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from config import settings


async_engine = create_async_engine(
    url=settings.DSN_postgresql_asyncpg, future=True, pool_size=50, max_overflow=100
)
session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_async_session():
    session_maker = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    async with session_maker() as session:
        yield session
        await session.commit()


# from typing import Protocol
# class ReadRepo(Protocol):
#     @classmethod
#     async def get_one(cls, session, id: int):
#         ...
#     @classmethod
#     async def get_many(cls, session, *args, **kwargs):
#         ...

# class WriteRepo(Protocol):
#     @classmethod
#     async def add_one(cls, session, id: int):
#         ...
#     @classmethod
#     async def add_many(cls, session, *args, **kwargs):
#         ...
