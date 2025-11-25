import asyncio
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from db_manager import DataBase
from picture_generator import PictureGenerator
from settings import settings


async def plot_hist(
        db: DataBase,
        max_date: datetime,
        age_distribution: pd.DataFrame,
) -> None:
    """
    Строит гистограммы распределения репозиториев по возрасту (в годах).
    """
    PictureGenerator.generate_histogram_picture(
        age_distribution["count"],
        "Распределение репозиториев по возрасту"
    )


async def main() -> None:
    db = DataBase(settings.db_url)
    age_distribution = await db.get_repository_lifespans()
    max_date = await db.max_date()

    await plot_hist(db, max_date, age_distribution)


if __name__ == "__main__":
    asyncio.run(main())