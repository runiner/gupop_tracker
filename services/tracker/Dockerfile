FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && \
    poetry install --no-dev

COPY . /app

EXPOSE 80

ENTRYPOINT ["/app/entrypoint.sh"]
