from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis

from routers.router import router as root
from config import settings

logging.basicConfig(level=logging.DEBUG, format=" %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    # await loading()
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(title="Spimex Trading Results", lifespan=lifespan)
app.include_router(root)
app.state.redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf8",
    decode_responses=True,
)

origins = [
    f"http://{settings.FRONTEND_HOST}:{settings.FRONTEND_PORT}",
    f"http://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


async def loading():
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    from database import async_engine
    from repos import repository as r
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
        logging.debug("data loading")
        dl = Downloader(after)
        rep = r.WriteItemRepo(session)
        await dl.download()
        for dayresult in dl.output:
            await rep.add_many(dayresult)
