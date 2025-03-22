import pandas as pd
import requests
import streamlit as st

from ragtube.api import Document, RAGError, get_rag_response
from ragtube.models import Channel
from ragtube.settings import get_settings
from ragtube.transcript import WATCH_URL

settings = get_settings()
API_URL = "http://{}:{}".format(
    settings.api_host.get_secret_value(), settings.api_port.get_secret_value()
)


st.title("💬 Chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hello! I am here to help answer any questions you may have about the YouTuber listed. Feel free to ask me anything, and I will provide you with accurate and helpful answers using transcriptions from their videos.",
        }
    ]

response = requests.get(f"{API_URL}/channel", timeout=5)
response.raise_for_status()
channels = [Channel.model_validate(channel) for channel in response.json()]

channel_selected = st.selectbox(
    "Filter by channel", (channel.title for channel in channels), index=None
)

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    params = {"input": st.session_state.messages[-1]["content"]}
    if channel_selected:
        for channel in channels:
            if channel.title == channel_selected:
                params["channel_id"] = channel.id
                break

    def stream():
        try:
            for response in get_rag_response(
                f"{API_URL}/rag",
                params=params,
            ):
                match response:
                    case None:
                        st.write("No relevant transcriptions were retrieved.")
                    case [Document(), *_]:
                        with st.expander("Context"):
                            df = pd.DataFrame(
                                document.model_dump() for document in response
                            )
                            df["video_id"] = df["video_id"].apply(
                                lambda x: WATCH_URL.format(video_id=x)
                            )
                            st.data_editor(
                                df,
                                column_config={
                                    "video_id": st.column_config.LinkColumn(
                                        "video_id"
                                    )
                                },
                                hide_index=True,
                            )
                        st.video(
                            WATCH_URL.format(video_id=response[0].video_id)
                        )
                    case str():
                        yield response
        except RAGError as e:
            st.error("An error occurred")
            st.json(e.response)

    st.write_stream(stream)
