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


async def plot_pie(
        db: DataBase
) -> None:
    """
    Строит круговые диаграммы распределения
    языков для репозиториев конкретного возраста
    """
    for age in [1, 2, 3, 5, 7, 10, 15, 18]:
        counts_languages = await db.get_language(age)
    counts_languages_top_10 = counts_languages.nlargest(10, "count")

    PictureGenerator.generate_pie_picture(
        counts_languages_top_10["count"], f"Языки в активных репозиториях {age} лет"
    )



async def main() -> None:
    db = DataBase(settings.db_url)
    age_distribution = await db.get_active_repository_lifespans()
    max_date = await db.max_date()
    for age in [1, 2, 3, 5, 7, 10, 15, 18]:
        counts_languages = await db.get_language(age)



    await plot_hist(db, max_date, age_distribution)
    await plot_pie(db, counts_languages)


if __name__ == "__main__":
    asyncio.run(main())