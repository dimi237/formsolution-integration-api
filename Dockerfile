FROM python:3.11-slim

WORKDIR /code

RUN pip install poetry

COPY pyproject.toml poetry.lock* /code/
RUN poetry install --no-root

COPY . /code

https://codeshare.io/ayPMWw
