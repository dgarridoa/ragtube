FROM python:3.11-slim-bookworm AS ragtube-base
COPY --from=ghcr.io/astral-sh/uv:0.6.5 /uv /uvx /bin/
RUN apt-get update && apt-get install -y curl
WORKDIR /app
RUN uv python pin 3.11
COPY . .

FROM ragtube-base AS ragtube
RUN uv sync

FROM ragtube-base AS ragtube-ci
RUN uv sync --all-extras
