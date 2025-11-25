import asyncio
import logging
from datetime import datetime

import tqdm
from dateutil.relativedelta import relativedelta

from db_manager import DataBase
from fetcher import ApiRateException, Fetcher
from settings import settings
from token_provider import TokenProvider


class App:
    def __init__(self, db: DataBase, fetcher: Fetcher, token_provider: TokenProvider) -> None:
        self.__db = db
        self.__fetcher = fetcher
        self.__tqdm: tqdm.tqdm | None = None
        self.__token_provider = token_provider


    def __get_request_count(self) -> int:
        """Количество страниц запроса"""
        per_page = self.__fetcher.per_page
        max_repos = settings.max_repos
        if max_repos % per_page == 0:
            return max_repos // per_page
        else:
            return max_repos // per_page + 1


    @staticmethod
    def __get_query(date: datetime) -> str:
        date_str = date.strftime("%Y-%m-%d")
        return f"fork:false stars:>15 size:>1024 created:{date_str}"


    async def search_and_save(self, query: str) -> None:
        """Функция проходится по всем страницам для одного запроса"""
        for page in range(1, self.__get_request_count() + 1):
            await self.search_and_save_page(query, page)



    async def search_and_save_by_day(self, date: datetime) -> None:
        """
        Функция проходится по всем дням за месяц и
        собирает репозитории, созданные в эти дни
        """
        end_date = date + relativedelta(months=1)
        while date < end_date:
            query = self.__get_query(date)
            await self.search_and_save(query)
            self.__tqdm.update(1)
            date = date + relativedelta(days=1)


    async def fetch_and_save_repos(self) -> None:
        """Сбор репозиториев по годам"""
        tasks = []
        end_date = datetime.now()
        current_date = end_date - relativedelta(years=settings.fetch_years) # дата старта
        total_steps = (end_date - current_date).days # число дней в промежутке
        self.__tqdm = tqdm.tqdm(total=total_steps, desc='Fetching')
        while current_date < end_date:
            next_date = current_date + relativedelta(months=1)
            tasks.append(self.search_and_save_by_day(next_date))
            current_date = next_date
        await asyncio.gather(*tasks)
        self.__tqdm.close()


    async def search_and_save_page(self, query: str, page: int) -> None:
        while True:
            try:
                logging.info(f"Токен доступа: {self.__fetcher.token.value}")
                infos = await self.__fetcher.fetch_repos_page(page, query) # тянем одну страницу из GitHub
                await self.__db.add_repo_info(infos) # сохраняем все репозитории этой страницы в базу

                if settings.debug:
                    counter = 1
                    for info in infos:
                        logging.info(f"{page}:{counter} Сохранен репозиторий {info}")
                        counter += 1

            except ApiRateException:
                logging.error(
                    f"Достигнут лимит запросов на странице {page}. Получение нового токена и перезапуск"
                )
                self.__fetcher.token.expired_at = datetime.now()
                self.__fetcher.token = await self.__token_provider.get_token()
                logging.error(f"Токен обновлен: {self.__fetcher.token.value}")
                continue

            except Exception as e:
                logging.error(f"Ошибка обработки страницы {page}, {e}")

            break


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        filename="app_log.log",
        filemode="w",
        encoding="utf-8",
        format="%(asctime)s%(levelname)s %(message)s",
    )
    db = DataBase(settings.db_url)
    await db.init()

    token_proivder = TokenProvider(settings.path_to_tokens)
    fetcher = Fetcher(await token_proivder.get_token())

    app = App(db, fetcher, token_proivder)
    await app.fetch_and_save_repos()


if __name__ == "__main__":
    asyncio.run(main())












