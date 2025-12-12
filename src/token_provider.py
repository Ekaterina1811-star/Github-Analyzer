import asyncio
import logging
from datetime import datetime


class Token:
    """
    Класс представляет один токен доступа,
    отслеживает, когда он был в последний раз использован.
    Attributes:
        value (str): Строковое значение токена, доступное только для чтения.
        expired_at (datetime | None): Время, когда токен был использован
        и стал временно недоступным. `None`, если токен "свежий".
    """
    def __init__(self, token: str) -> None:
        self.__value = token
        self.__expired_at: datetime | None = None


    @property
    def value(self) -> str:
        """Возвращает строковое значение токена."""
        return self.__value


    @property
    def expired_at(self) -> datetime | None:
        return self.__expired_at


    @expired_at.setter
    def expired_at(self, expired_at: datetime) -> None:
        """Устанавливает время 'истечения' токена после его использования."""
        self.__expired_at = expired_at


class NoTokenAvailable(Exception):
    pass


class TokenProvider:
    """
    Управляет токенами.

    Attributes:
        __tokens (list[Token]): Список загруженных объектов Token.
    """
    def __init__(self, path: str) -> None:
        self.__tokens = self.__get_tokens(path)


    @staticmethod
    def __get_tokens(path: str) -> list[Token]:
        """
        Загружает токены из файла.

        Args:
            path (str): Путь к файлу с токенами.

        Returns:
            list[Token]: Список объектов Token. Пустой список, если
                файл не найден или пуст.
        """
        tokens = []
        try:
            with open(path, "r") as file:
                for line in file.readlines():
                    token_str = line.strip()
                    if token_str:
                        tokens.append(Token(token=token_str))
        except FileNotFoundError:
            logging.info(f"Ошибка при чтении токенов из файла: {path} не найден.")
        except Exception as e:
            logging.info(f"Ошибка при чтении файла: {e}")

        return tokens


    async def get_token(self) -> Token:
        """
        Асинхронно получает следующий доступный токен из пула.

        Returns:
            Token: Объект токена, готовый к использованию.
        """
        while True:
            for token in self.__tokens:
                if token.expired_at is None:
                    return token
                if (datetime.now() - token.expired_at).total_seconds() >= 3660:
                    token.expired_at = None
                    return token
                continue
            await asyncio.sleep(3660)

