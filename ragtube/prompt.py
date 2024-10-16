from langchain.prompts import PromptTemplate


def get_prompt() -> PromptTemplate:
    TEMPLATE = """You will be asked questions about a YouTuber named ThePrimeagen. His content is related to software engineering.
    I will provide you with transcriptions from his videos to use as context to answer the question at the end.

    <context>
    {context}
    </context>

    Question: {input}

    Answer:
    """
    prompt = PromptTemplate(
        template=TEMPLATE, input_variables=["context", "input"]
    )
    return prompt
