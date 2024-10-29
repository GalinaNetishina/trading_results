import os
from pathlib import Path
import pytest
from datetime import datetime, timedelta
from trading_result_app.utils import Downloader
from trading_result_app.models.models import Item
from sqlalchemy.orm import DeclarativeBase


class TestDownloader:
    @pytest.mark.parametrize("date", ["01.10.2024", "01.01.2024"])
    def test_creating_with_correct_dates(self, date):
        dl = Downloader(date)
        assert dl.start == datetime.strptime(date, "%d.%m.%Y").date()

    @pytest.mark.parametrize("date", ["01-10-2024", "07.13.2025", "01.10.2026"])
    def test_creating_with_wrong_dates(self, date):
        default = Downloader().start
        dl = Downloader(date)
        assert dl.start == default

    @pytest.mark.skipif("config.getoption('--run-slow') == 'false'")
    async def test_fetch_files(self):
        date = datetime.strftime((datetime.today() - timedelta(days=5)), "%d.%m.%Y")
        dl = Downloader(date)
        await dl.produce()
        for file in os.listdir(os.path.join(Path.cwd(), "temp")):
            assert (
                dl.start
                <= datetime.strptime(file[:-4], "%Y%m%d").date()
                <= datetime.today().date()
            )
            
    @pytest.mark.skipif("config.getoption('--run-slow') == 'false'")
    async def test_loading(self):
        date = datetime.strftime((datetime.today() - timedelta(days=5)), "%d.%m.%Y")
        dl = Downloader(date)
        await dl.produce()
        files_count = len(os.listdir(os.path.join(Path.cwd(), "temp")))
        await dl.consume()
        assert len(os.listdir(os.path.join(Path.cwd(), "temp"))) == 0
        assert len(dl.output) == files_count
        for item in dl.output.pop():
            # assert isinstance(item, Item)
            assert issubclass(type(item), DeclarativeBase)
        
