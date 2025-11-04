import pandas as pd
import uuid
from datetime import datetime
from typing import Optional

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


class DateBase:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, echo=False)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)



    async def init(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)


    async def add_repo_info(self, infos: list[RepoInfo]) -> None:
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


    async def get_repository_lifespans(
            self,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
    ) -> pd.DataFrame:
        if date_from is None:
            date_from = await self.min_date()

        if date_to is None:
            date_to = await self.max_date()

        async with (self.session() as session):
            async with session.begin():
                lifespan_days_expr = func.julianday(RepoInfo.pushed_at) - func.julianday(RepoInfo.created_at)



