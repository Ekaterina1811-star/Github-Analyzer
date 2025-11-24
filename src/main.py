import asyncio
import logging

from db_manager import DateBase
from fetcher import ApiRateException, Fetcher
from save_data import App
from settings import settings
from token_provider import TokenProvider


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        filename="app_log.log",
        filemode="w",
        encoding="utf-8",
        format="%(asctime)s%(levelname)s %(message)s",
    )
    db = DateBase(settings.db_url)
    await db.init()

    token_proivder = TokenProvider(settings.path_to_tokens)
    fetcher = Fetcher(await token_proivder.get_token())

    app = App(db, fetcher, token_proivder)
    await app.fetch_and_save_repos()


if __name__ == "__main__":
    asyncio.run(main())