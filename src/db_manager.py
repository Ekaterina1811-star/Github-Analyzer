import pandas as pd
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import Field, SQLModel, select, func

from settings import settings


ACTIVE_AFTER = settings.active_date


class RepoInfo(SQLModel, table=True):
    repo_id: int = Field(primary_key=True)
    full_name: str = Field(index=True)
    language: Optional[str] = Field(index=True)
    created_at: datetime
    pushed_at: datetime
    stars_count: int
    forks_count: int
    age_years: Optional[int] = None


class DataBase:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=False)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)


    async def init(self) -> None:
        """Создает в базе данных таблицу"""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)


    async def add_repo_info(
            self,
            infos: list[RepoInfo],
    ) -> None:
        """Добавляет объекты RepoInfo в таблицу в базе данных"""
        async with self.session() as session:
            async with session.begin():
                now = datetime.now()
                for info in infos:
                    if info.pushed_at > ACTIVE_AFTER:
                        info.age_years = (now - info.created_at).days // 365
                infos = [RepoInfo.model_validate(info) for info in infos]
                session.add_all(infos)
                await session.commit()


    async def min_date(self) -> datetime:
        """
        Функция находит дату создания самого раннего репозитория.
        """
        async with self.session() as session:
            async with session.begin():
                query = select(func.min(RepoInfo.created_at))
                result = await session.execute(query)
                return result.scalar()


    async def max_date(self) -> datetime:
        """
        Функция находит дату создания самого позднего репозитория.
        """
        async with self.session() as session:
            async with session.begin():
                query = select(func.max(RepoInfo.created_at))
                result = await session.execute(query)
                return result.scalar()


    async def get_active_repository_lifespans(
            self,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Функция считает, сколько репозиториев живет 1, 2, 3... лет
        от сегодняшнего момента - у которых последний коммит после
        даты active_after
        """
        if date_from is None:
            date_from = await self.min_date()

        if date_to is None:
            date_to = await self.max_date()

        async with self.session() as session:
            async with session.begin():
                query = (
                    select(RepoInfo.age_years, func.count())
                    .where(RepoInfo.pushed_at > ACTIVE_AFTER)
                    .where(RepoInfo.created_at.between(date_from, date_to))
                    .group_by(RepoInfo.age_years)
                    )
                result = await session.execute(query)
                dataframe = pd.DataFrame(
                    result.all(),
                    columns=["age_years", "count"]
                )
                dataframe.set_index("age_years", inplace=True)
                return dataframe


    async def get_language(
            self,
            age: int,
            active_after: datetime = datetime(2024, 1, 1),
    ) -> pd.DataFrame:
        """
        Возвращает топ языков для репозиториев конкретного возраста.
        :param age: Возраст репозитория
        :param active_after: учитывает репозитории, последний коммит которых
        сделан после указанной даты
        :return: DataFrame со столбцами: language, count
        """
        async with self.session() as session:
            async with session.begin():
                query = (
                    select(RepoInfo.language, func.count())
                    .where(RepoInfo.language.isnot(None))
                    .where(RepoInfo.age_years == age)
                    .where(RepoInfo.pushed_at > active_after)
                    .group_by(RepoInfo.language)
                )
                result = await session.execute(query)
                dataframe = pd.DataFrame(
                    result.all(),
                    columns=["language", "count"]
                )
                dataframe.set_index("language", inplace=True)
                return dataframe


    async def get_count_last_push(self) -> pd.DataFrame:
        """
        Возвращает, сколько репозиториев
        сделали свой последний коммит в каждом году
        """
        async with self.session() as session:
            async with session.begin():
                # year_of_last_push = func.strftime('%Y', RepoInfo.pushed_at).label("year")

                query = (
                    select(
                        func.strftime("%Y", RepoInfo.pushed_at).label("year"),
                        func.count(),
                    )
                    .group_by("year")
                )
                result = await session.execute(query)
                dataframe = pd.DataFrame(
                    result.all(),
                    columns=["year", "count"]
                )
                dataframe.set_index("year", inplace=True)
                return dataframe



