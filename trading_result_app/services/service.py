from datetime import datetime, timedelta
from starlette.exceptions import HTTPException
from sqlalchemy import desc
from repos.repository import ReadItemRepo, ReadDaysRepo, WriteItemRepo

from utils import Downloader


class ItemService:
    def __init__(self, session):
        self.repo = ReadItemRepo(session)

    async def get_item_by_id(self, id: int):
        res = await self.repo.get_one(id)
        if not res:
            raise HTTPException(status_code=404, detail=f"Item #{id} not found")
        return res

    async def get_items(self, filter, limit, skip):
        return await self.repo.get_many(filter, limit, skip, order_by=desc("date"))

    async def get_dynamic(self, filter, limit, skip):
        return await self.repo.get_dynamic(filter, limit, skip, order_by="date")


class DaysService:
    def __init__(self, session):
        self.repo = ReadDaysRepo(session)

    async def get_days(self, count: int):
        return await self.repo.get_many(count)

    async def get_day(self):
        return await self.repo.get_one()


class LoadService:
    def __init__(self, session, default_start="01.10.2024"):
        self.sub_serv = DaysService(session)
        self.repo = WriteItemRepo(session)
        self.start = default_start

    @property
    async def is_loading_needed(self):
        last_day = await self.sub_serv.get_day()
        if not last_day:
            return True
        self.start = last_day.date.strftime("%d.%m.%Y")
        return datetime.now().date() - last_day.date > timedelta(days=3)

    async def load(self):
        dl = Downloader(self.start)
        await dl.download()
        for data in dl.output:
            await self.repo.add_many(data)
