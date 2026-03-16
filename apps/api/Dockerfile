FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . /app

RUN uv pip install --system -e .[dev]

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
