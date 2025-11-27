from datetime import datetime
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str
    debug: bool = True
    path_to_tokens: str
    max_repos: int = 1000
    fetch_years: int = 18
    active_after: str = "2024-01-01" # Дата, после которой у репозитория есть коммиты
    model_config = SettingsConfigDict(env_file='../.env')


    @property
    def active_date(self) -> datetime:
        """Преобразует строку в datetime"""
        return datetime.strptime(self.active_after, "%Y-%m-%d")


settings = Settings()