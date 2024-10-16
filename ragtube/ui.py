import pandas as pd
import streamlit as st

from ragtube.api import RAGError, RAGOutput, get_rag_response
from ragtube.settings import get_settings
from ragtube.transcript import WATCH_URL

settings = get_settings()
RAG_URL = "http://{}:{}/rag".format(
    settings.api_host.get_secret_value(), settings.api_port.get_secret_value()
)


st.title("💬 Chatbot")
st.caption("🚀 RAG powered by LLama 3.1")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hello! I'm here to help you with any questions you have about [ThePrimeagen](https://www.youtube.com/@ThePrimeTimeagen), a YouTuber who creates content related to software engineering. Feel free to ask me anything, and I'll use transcriptions from his videos to provide you with accurate and helpful answers.",
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = get_rag_response(
        RAG_URL,
        settings.api_user.get_secret_value(),
        settings.api_password.get_secret_value(),
        st.session_state.messages[-1]["content"],
    )

    match response:
        case RAGError():
            st.error("An error occurred")
            st.json(response.response)
        case RAGOutput():
            st.session_state.messages.append(
                {"role": "assistant", "content": response.answer}
            )
            st.chat_message("assistant").write(response.answer)
            with st.expander("Context"):
                df = pd.DataFrame(
                    [document.model_dump() for document in response.context]
                )
                df["video_id"] = df["video_id"].apply(
                    lambda x: WATCH_URL.format(video_id=x)
                )
                st.data_editor(
                    df,
                    column_config={
                        "video_id": st.column_config.LinkColumn("video_id")
                    },
                    hide_index=True,
                )
            st.video(WATCH_URL.format(video_id=response.context[0].video_id))
