FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del .build-deps

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]