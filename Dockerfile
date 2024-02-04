# syntax=docker/dockerfile:1.6

FROM python:3.11-slim-buster

ENV TZ=UTC

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    git \
    iputils-ping \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY requirements.txt .

ENV DATABASE_NAME=${POSTGRES_DB:-postgres}
ENV DATABASE_URL=${POSTGRES_HOST:-db}
ENV DATABASE_USER=${POSTGRES_USER:-postgres}
ENV DATABASE_PASSWORD=${POSTGRES_PASSWORD}
ENV DATABASE_PORT=${POSTGRES_PORT:-5432}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

RUN python -m pip install --no-cache-dir -r requirements.txt

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

ENV WEB_CONCURRENCY=2

COPY . .

EXPOSE 8000

ENTRYPOINT [ "/app/startup.sh" ]
