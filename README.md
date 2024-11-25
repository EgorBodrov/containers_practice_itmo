# Lab 2

## TODO

- [x] Собрать compose проект
- [x] Добавить минимум 3 сервиса один из которых init.
- [x] Добавить автоматическую сборку контейнеров из Dockerfile
- [x] Добавить жесткое именование сервисам
- [x] Добавить `depends_on`
- [x] Добавить `volume`
- [x] Добавить проброс портов наружу
- [x] Добавить ключ command и/или entrypoint
- [x] Добавить healthcheck
- [x] Вынести ENV из докер файлов в `.env`
- [x] Указать network одну на всех


## Содержимое docker-compose.yaml

Файл `docker-compose.yaml` содержит в себе 4 сервиса:
> **qdrant**. Векторное хранилище
- Выкачивается из qdrant image из облака
- Дополнительно устанавливается `curl`
- Используем healthcheck на корректность запуска

> **qdrant_init**. Инит контейнер
- Запускается только в случае `healthy` статуса qdrant
- Выполняет преобразование данных в эмбеддинги и сохранение в qdrant

> **backend**. Backend сервис
- Запускается только если `healthy` qdrant и закончено заполнение инит-контейнером
- Содержит доп-переменные среды для использования (ключи для OpenAI из `.env` файла)
- Внутри себя запускает FastAPI приложение вместе с LLM-агентом
- История диалога хранится отдельно, использован volume

> **frontend**. Frontend сервис
- Зависит от backend
- Streamlit приложение которое отправляет post-запрос в backend и отображает диалог

## Ответы на вопросы
1. **Можно ли ограничивать ресурсы (например, память или CPU) для сервисов в docker-compose.yml? Если нет, то почему,
если да, то как?**
> Можно установить лимиты на использование CPU и RAM. Для этого нужно использовать ключи `deploy.resources` и установить limits
> или reservations
> ```docker-compose.yaml
> version: "3.9"
>services:
>  app:
>    image: my-app
>    deploy:
>      resources:
>        limits:
>          cpus: "0.5" # Ограничить использование процессора до 50%
>          memory: "512M" # Ограничить использование памяти до 512 МБ
>        reservations:
>          cpus: "0.25" # Минимальный резерв процессора 25%
>          memory: "256M" # Минимальный резерв памяти 256 МБ
> ```

2. **Как можно запустить только определенный сервис из docker-compose.yml, не запуская остальные?**
> Можно запустить, используя имя сервиса/ов для запуска конкретных сервисов, установить флаг `--no-deps` если они зависят от других сервисов
> ```shell
> docker compose up <service_name>
> ```

## To run

```shell
docker compose up -d
```
# containers_project
