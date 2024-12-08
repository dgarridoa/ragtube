FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu24.04 AS ragtube-base
WORKDIR /app
RUN apt update && apt install -y curl
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.cargo/bin/:$PATH"
RUN uv python install 3.11
RUN uv python pin 3.11
COPY . .

FROM ragtube-base AS ragtube
RUN uv sync

FROM ragtube-base AS ragtube-ci
RUN uv sync --all-extras

FROM ollama/ollama AS ollama
RUN apt update && apt install -y curl
WORKDIR /app
COPY run-ollama.sh params.yaml .
RUN chmod +x run-ollama.sh && ./run-ollama.sh
