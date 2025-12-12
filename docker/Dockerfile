FROM python:3.10.12

WORKDIR /app

# Устанавливаем uv
RUN pip install uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock .

# Устанавливаем зависимости через uv
RUN uv sync

# Копируем entry-point скрипт
COPY docker/entry.sh .

RUN chmod +x entry.sh

ENTRYPOINT ["./entry.sh"]