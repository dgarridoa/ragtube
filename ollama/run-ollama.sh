#!/bin/bash

echo "Starting Ollama server..."
ollama serve &

echo "Waiting for Ollama server to be active..."
while [ "$(ollama list | grep 'NAME')" == "" ]; do
  sleep 1
done

ollama pull $(sed -n 's/.*chat_model_name: *"\?\([^"]*\)"\?/\1/p' params.yaml)
ollama pull $(sed -n 's/.*embedding_model_name: *"\?\([^"]*\)"\?/\1/p' params.yaml)
