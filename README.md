# Lab 1

## TODO

- [x] Написать bad Dockerfile
- [x] Написать good Dockerfile
- [x] Расписать 3 bad practices в плохом Dockerfile и как они были исправлены
- [x] Два случая когда не стоит использовать контейнеры
- [x] VOLUME внутри Dockerfile

## Bad Dockerfile

На примере `backend` части приложения

```Dockerfile
FROM python:3.12 AS builder

WORKDIR /app

COPY . . 
RUN python -m pip install --no-cache-dir poetry 
RUN poetry config virtualenvs.in-project true
RUN poetry install

FROM python:3.12
COPY --from=builder /app /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app/backend

VOLUME /app/backend/data

EXPOSE 4242

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "4242"]

```

## Что не так

1. Используется общий базовый образ python:3.12 на всех stage сборки, что увеличивает размер образа. Также не установлена конкретная версия poetry, это может сломать обратную совместимость. **Необходимо конкретизировать версии.**

2. Копируются абсолютно все директории и папки внутрь образа, что не нужно в данном случае, поскольку мы разворачиваем backend отдельно от frontend. Аналогично с этим, мы устанавливаем внутри poetry сразу весь список зависимостей (например streamlit), который не будет использоваться внутри приложения backend. **Необходимо разделить ответственность и сохранять в образе только нужные под конкретное приложение зависимости и файлы.**

3. Создается множество лишних слоев в Dockerfile.bad, а команды установки зависимостей могут быть объединены в одну строчку.

## Good Dockerfile

```Dockerfile
FROM python:3.12-slim-bullseye AS builder

WORKDIR /app
ENV POETRY_VERSION=1.8.3

COPY backend/ backend/
COPY agent/ agent/
COPY .env poetry.lock pyproject.toml README.md .
RUN python -m pip install --no-cache-dir poetry==$POETRY_VERSION \
    && poetry config virtualenvs.in-project true \
    && poetry install --without frontend

FROM python:3.12-slim-bullseye
COPY --from=builder /app /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app/backend

VOLUME /app/backend/data

EXPOSE 4242

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "4242"]
```

## Что поменялось

1. Конкретизированы версии образа python:3.12-slim-bullseye, установлена конкретная версия poetry.

2. Используем установку только необходимых зависимостей, исключая группу frontend. Также копируем только нужные для запуска backend директории приложения.

3. Установка зависимостей через pip вынесена в одну общую строку в рамках одного слоя Dockerfile.

## Containers bad practices

- **Использование микросервисной архитектуры, когда она не нужна**. В рамках простого приложения нет надобности разбивать его на микросервисы. Некоторые программные решения могут существовать в рамках монолитной структуры, которая не требует разбиения на отдельные контейнеры, что в свою очередь приводит к тратам лишних ресурсов и усилий разработчиков. 

- **Хранение данных внутри контейнера**. В случаях хранения данных внутри запущенного контейнера, мы рискуем потерять данные например когда контейнер упадет или остановится. Для этого следует записывать данные на том, следить за тем чтобы разные контейнеры не затирали информацию друг друга.

## To run

```shell
docker build -f docker/backend/Dockerfile -t backend_service .
docker run -p 4242:4242 -d -v $(pwd)/backend/data:/app/backend/data backend_service
```
# containers_project