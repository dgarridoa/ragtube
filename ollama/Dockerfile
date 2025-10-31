FROM ollama/ollama AS ollama
RUN apt update && apt install -y curl
WORKDIR /app
COPY run-ollama.sh .
RUN chmod +x run-ollama.sh
ENTRYPOINT ["sh", "-c", "./run-ollama.sh && tail -f /dev/null"]
