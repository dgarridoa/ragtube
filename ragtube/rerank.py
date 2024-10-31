from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from langchain_core.retrievers import RetrieverLike


def get_rerank(
    retriever: RetrieverLike,
    results_to_retrieve: int = 5,
    score_threshold: float = 0.1,
    model_name: str = "rank-T5-flan",
):
    compressor = FlashrankRerank(
        top_n=results_to_retrieve,
        score_threshold=score_threshold,
        model=model_name,
    )
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=retriever
    )
    return compression_retriever
