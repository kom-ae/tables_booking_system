FROM python:3.11-alpine

WORKDIR /app

# Ставим runtime-библиотеки и build-зависимости
RUN apk add --no-cache \
    postgresql-libs \
    libffi \
    openssl \
 && apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    postgresql-dev \
    build-base

COPY src/requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

RUN apk del .build-deps

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY entrypoint.sh .
COPY create_superuser_cli.py .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["sh", "entrypoint.sh"]
