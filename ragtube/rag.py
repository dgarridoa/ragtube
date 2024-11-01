from functools import lru_cache

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.language_models import LanguageModelLike
from langchain_core.prompts import BasePromptTemplate
from langchain_core.retrievers import BaseRetriever

from ragtube.chat import get_ollama_model
from ragtube.database import setting_engine
from ragtube.embedding import get_bge_embedding_model
from ragtube.params import get_params
from ragtube.prompt import get_prompt
from ragtube.rerank import get_rerank_retriever
from ragtube.retriever import Retriever


def create_rag_chain(
    llm: LanguageModelLike,
    retriever: BaseRetriever,
    prompt: BasePromptTemplate,
):
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, question_answer_chain)
    return chain


@lru_cache
def get_rag_chain(channel_id: str | None = None):
    params = get_params()
    chat_model = get_ollama_model(
        params.chat_model_name, params.chat_temperature, params.chat_max_tokens
    )
    embedding_model = get_bge_embedding_model(
        params.embedding_model_name,
        params.embedding_model_kwargs,
        params.embedding_encode_kwargs,
    )
    retriever = Retriever(
        engine=setting_engine(),
        embedding_model=embedding_model,
        results_to_retrieve=params.results_to_retrieve,
        channel_id=channel_id,
    )
    rerank_retriever = get_rerank_retriever(
        retriever,
        params.results_to_retrieve,
        params.rerank_score_threshold,
        params.rerank_model_name,
    )
    prompt = get_prompt()
    rag_chain = create_rag_chain(chat_model, rerank_retriever, prompt)
    return rag_chain
