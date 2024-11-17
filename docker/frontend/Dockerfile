FROM python:3.12-slim-bullseye AS builder

WORKDIR /app
ENV POETRY_VERSION=1.8.3

COPY frontend/ frontend/
COPY poetry.lock pyproject.toml .
RUN python -m pip install --no-cache-dir poetry==$POETRY_VERSION \
    && poetry config virtualenvs.in-project true \
    && poetry install --only frontend --no-root

FROM python:3.12-slim-bullseye
COPY --from=builder /app /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app/frontend

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501"]