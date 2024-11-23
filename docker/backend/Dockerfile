FROM python:3.12-slim-bullseye AS builder

WORKDIR /app
ARG POETRY_VERSION

COPY backend/ backend/
COPY agent/ agent/
COPY poetry.lock pyproject.toml README.md .
RUN python -m pip install --no-cache-dir poetry==$POETRY_VERSION \
    && poetry config virtualenvs.in-project true \
    && poetry install --without frontend

FROM python:3.12-slim-bullseye
COPY --from=builder /app /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app/backend

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "4242"]