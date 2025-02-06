from typing import List

from langchain_core.messages import BaseMessage, HumanMessage
from google.cloud import firestore
import streamlit as st

from modules.firestore_manager import add_message
from graph.streaming import stream_graph
from graph.llm import llm 


def create_messages(displayed_chat_messages) -> List[BaseMessage]:
    """
    LLMに送るためのメッセージのリストを作成する関数
    """
    messages = []
    for data in displayed_chat_messages:
        message = HumanMessage(content=data['content'])
        messages.append(message)
    return messages

def create_title(user_input_text: str):
    chat_title_prompt = f"""
    ChatBotとの会話を開始するためにユーザーが入力した文を与えるので、その内容を要約し会話のタイトルを考えてもらいます。
    出力は、会話のタイトルのみにしてください。
    ユーザーの入力文: {user_input_text} """
    displayed_chat_title = llm.invoke(chat_title_prompt).content.strip()
    return displayed_chat_title
    
def chat_mbtibot(messages,
                 max_retry_count: int,
                 displayed_chat_messages: list,
                 displayed_chat_ref: firestore.DocumentReference,
                 user_name: str
                 ):
    # MBTIのメッセージを一人ずつストリーミングで取り出す。
    for message, search_web_list in stream_graph(messages, max_retry_count, user_name):
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(message)
            for num, search_web in enumerate(search_web_list):
                if num == 0:
                    message += "\n\n参考情報:"
                    message_placeholder.markdown(message)
                message += f"[{search_web.title}]({search_web.uri})\n"
                message_placeholder.markdown(message)
        # llmの返答をセッションステートとFirestoreに格納
        assistant_output_data = {
            "role": "assistant",
            "content": message,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        displayed_chat_messages.append(assistant_output_data)
        if displayed_chat_ref:
            add_message(displayed_chat_ref, assistant_output_data)
    st.session_state.displayed_chat_messages = displayed_chat_messages


