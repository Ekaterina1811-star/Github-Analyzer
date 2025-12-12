# GitHub-Analyzer - приложение, анализирующее активность репозиториев GitHub

***

## Технологии:

[![Python](https://img.shields.io/badge/Python-%203.10-blue?style=flat-square&logo=Python)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-%2024.0.5-blue?style=flat-square&logo=docker)](https://www.docker.com/)

***

## Анализ активности репозиториев GitHub за период 2008-2025 годы.

***

## Описание

Проект собирает данные о репозиториях с GitHub API, сохраняет в SQLite базу данных и строит визуализации:
- Распределение активных репозиториев по годам создания
- Популярность языков программирования
- Гистограмма распределения создания репозиториев по годам создания
- Гистограмма распределения последнего коммита репозиториев по годам

***

## Запуск проекта локально в Docker-контейнерах с помощью Docker

Склонируйте проект из репозитория:

```shell
git clone https://github.com/Ekaterina1811-star/Github-Analyzer.git
```


Перейдите в директорию проекта:

```shell
cd Github-Analyzer/
```

Создайте файл .env:

```shell
nano .env
```

Добавьте строки, содержащиеся в файле **.env.example** и подставьте 
свои значения.

Пример из .env файла:

```dotenv
# Путь к файлу базы данных относительно корня проекта
DB_URL="sqlite+aiosqlite:///./data.db"
# Путь к файлу с токенами относительно корня проекта
PATH_TO_TOKENS="github_tokens.txt"
DEBUG="true"
MAX_REPOS=1000
FETCH_YEARS=18 # Количество лет, за которые нужно загрузить данные
ACTIVE_AFTER="2024-01-01" # Дата, после которой у репозитория есть коммиты
```

Создайте файл github_tokens.txt:

```shell
nano github_tokens.txt
```

Пропишите в этом файле токены доступа к GitHub API. Каждый токен должен быть написан на новой строке. 
Запятых, точек, лишних пробелов быть не должно. Токен можно получить в настройках вашего аккаунта на GitHub.
Один токен позволяет сделать 5000 запросов в час.

Пример из файла github_tokens.txt:

```dotenv
token1
token2
token3
```

Соберите Docker изображение:

```shell
sudo docker build -t github_analyzer -f docker/Dockerfile .
```

Запустите процесс сборки данных:

```shell
sudo docker run --rm -it -v ./src:/app/src -v .env:/app/.env github_data:latest save
```

Запустите процесс построения графиков. Графики будут находиться в папке src/media:

```shell
sudo docker run --rm -it -v ./src:/app/src -v .env:/app/.env github_data:latest analyze
```

***

## Автор

[**Екатерина Старунская**](https://github.com/Ekaterina1811-star)



