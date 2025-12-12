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
        title: str,
        x_title: str,
        y_title: str,
        age_distribution: pd.DataFrame,
) -> None:
    """
    Строит гистограммы распределения репозиториев по возрасту (в годах).
    """
    PictureGenerator.generate_histogram_picture(
        age_distribution["count"],
        title,
        x_title,
        y_title,
    )


async def plot_pie(
        db: DataBase
) -> None:
    """
    Строит круговые диаграммы распределения
    языков для репозиториев конкретного возраста
    """
    for age in [2025, 2024, 2023, 2022, 2021, 2020, 2018, 2016, 2012, 2010]:
        counts_languages = await db.get_language(age)
        counts_languages_top_10 = counts_languages.nlargest(10, "count")

        PictureGenerator.generate_pie_picture(
            counts_languages_top_10["count"], f"Языки в активных репозиториях c {age} года"
        )


async def plot_lines(
        db: DataBase,
        max_date: datetime,
        counts_last_year: pd.DataFrame,
) -> None:
    """Строит линейный график"""
    pass


async def main() -> None:
    db = DataBase(settings.db_url)
    age_distribution = await db.get_active_repository_lifespans()
    max_date = await db.max_date()
    push_distribution = await db.get_count_last_push()
    create_distribution = await db.get_count_created_repo()
    await plot_hist(
        db,
        max_date,
        "Распределение репозиториев по возрасту",
        "Года создания",
        "Количество репозиториев",
        age_distribution,
    )
    await plot_pie(db)
    await plot_hist(
        db,
        max_date,
        "Последние коммиты репозиториев по годам",
        "Года",
        "Количество репозиториев",
        push_distribution,
    )
    await plot_hist(
        db,
        max_date,
        "Количество созданных репозиториев в каждый год",
        "Года",
        "Количество репозиториев",
        create_distribution
    )


if __name__ == "__main__":
    asyncio.run(main())
