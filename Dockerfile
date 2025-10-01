FROM python:3.13-slim

WORKDIR /code

RUN pip install poetry

COPY pyproject.toml poetry.lock* /code/
RUN poetry install --no-root

COPY . /code

EXPOSE 4000

CMD ["poetry", "run", "start"]


