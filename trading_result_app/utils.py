import asyncio
from collections import deque
import datetime
import logging
import os

import aiohttp
import xlrd
from typing import Iterator
from datetype import _date as d
import aiofiles

from models.models import Item


async def write_file(filename, data):
    async with aiofiles.open(filename, "wb") as file:
        await file.write(data)


class Downloader:
    def __init__(self, start: str = "01.01.2023"):
        self.start: datetime.date
        try:
            self.start = datetime.datetime.strptime(start, "%d.%m.%Y").date()
            if self.start > datetime.datetime.today().date():
                raise ValueError
        except ValueError:
            self.start = datetime.datetime.strptime("01.01.2023", "%d.%m.%Y").date()
        self.output_dir = "temp"
        os.makedirs("temp", exist_ok=True)
        self.process = asyncio.Queue()
        self.output = deque()

    async def download(self) -> None:
        await asyncio.gather(self.produce())
        await asyncio.gather(self.consume())

    async def produce(self) -> None:
        async with aiohttp.ClientSession() as session:
            end = datetime.datetime.today().date()
            for i in range((end - self.start).days + 1):
                file = await self._fetch_file(
                    self.start + datetime.timedelta(days=i), session
                )
                if not file:
                    continue
                await self.process.put(file)
                logging.info(f"produce...{file}")
            await self.process.put(None)

    async def consume(self) -> None:
        while True:
            item = await self.process.get()
            if item is None:
                break
            logging.info(f"consume...{item}")
            self.extract_items(item)
            os.remove(item)

    @staticmethod
    async def _fetch_file(date: d, session) -> str:
        url = f'https://spimex.com//upload/reports/oil_xls/oil_xls_{date.strftime("%Y%m%d")}162000.xls'
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                filename = os.path.join("temp", f'{date.strftime("%Y%m%d")}.xls')
                await write_file(filename, data)
                return filename

    def extract_items(self, file: str) -> Iterator[Item]:
        xls = xlrd.open_workbook_xls(file)
        sheet = xls.sheet_by_index(0)

        def is_not_ordered(*args: str) -> bool:
            return any(not i.isdigit() for i in args)

        def get_int(str_digit: str) -> int:
            try:
                return int(str_digit)
            except Exception:
                return int(float(str_digit) * 1000)

        dayresult = []

        for i in range(8, sheet.nrows - 2):
            _, id, name, basis, *tail = (sheet[i][j].value for j in range(sheet.ncols))
            volume, total, count = tail[0], tail[1], tail[5]
            date = datetime.datetime.strptime(file[-12:-4], "%Y%m%d").date()
            if is_not_ordered(volume, total, count):
                continue
            dayresult.append(
                Item(
                    exchange_product_id=id,
                    exchange_product_name=name.split(",")[0],
                    oil_id=id[:4],
                    delivery_basis_id=id[4:7],
                    delivery_basis_name=basis,
                    delivery_type_id=id[-1],
                    volume=get_int(volume),
                    total=get_int(total),
                    count=get_int(count),
                    date=date,
                )
            )
        self.output.append(dayresult)
