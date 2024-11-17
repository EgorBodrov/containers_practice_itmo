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