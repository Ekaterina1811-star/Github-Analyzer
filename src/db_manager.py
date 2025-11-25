import pandas as pd
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import Field, SQLModel, select, func


class RepoInfo(SQLModel, table=True):
    repo_id: int = Field(primary_key=True)
    full_name: str = Field(index=True)
    language: Optional[str] = Field(index=True)
    created_at: datetime
    pushed_at: datetime
    contributors_count: Optional[int] = Field(default=None)
    stars_count: int
    forks_count: int


class DataBase:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=False)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)


    async def init(self) -> None:
        """Создает в базе данных таблицу"""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)


    async def add_repo_info(self, infos: list[RepoInfo]) -> None:
        """Добавляет объекты RepoInfo в таблицу в базе данных"""
        async with self.session() as session:
            async with session.begin():
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
            date_to: Optional[datetime] = None,
            active_after: datetime = datetime(2024, 1, 1),
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
                age_years = func.cast(
                    (func.julianday("now") - func.julianday(RepoInfo.created_at)) / 365, Integer
                ).label("age_years")
                #lifespan_days = func.julianday(RepoInfo.pushed_at) - func.julianday(RepoInfo.created_at)
                query = (
                    select(age_years, func.count())
                    .where(RepoInfo.pushed_at > active_after)
                    .where(RepoInfo.created_at.between(date_from, date_to))
                    .group_by(age_years)
                    )
                result = await session.execute(query)
                dataframe = pd.DataFrame(
                    result.all(),
                    columns=["age_years", "count"]
                )
                dataframe.set_index("age_years", inplace=True)
                return dataframe





