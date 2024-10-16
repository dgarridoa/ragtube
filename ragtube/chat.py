from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama


def get_ollama_model(
    model_name: str = "llama3.1:8b",
    temperature: float = 0.0,
    max_tokens: int = 500,
) -> ChatOllama:
    llm = ChatOllama(
        model=model_name, temperature=temperature, num_predict=max_tokens
    )
    return llm


def query_chat_model(chat_model: BaseChatModel, query: str) -> BaseMessage:
    return chat_model.invoke(query)
