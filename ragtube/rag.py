from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.language_models import LanguageModelLike
from langchain_core.prompts import BasePromptTemplate
from langchain_core.retrievers import BaseRetriever


def create_rag_chain(
    llm: LanguageModelLike,
    retriever: BaseRetriever,
    prompt: BasePromptTemplate,
):
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, question_answer_chain)
    return chain
