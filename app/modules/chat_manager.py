from typing import List

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from google.cloud import firestore
import streamlit as st

from modules.firestore_manager import add_chat, add_message
from graph.streaming import stream_graph
from graph.llm import llm 


def create_messages(displayed_chat_messages) -> List[BaseMessage]:
    """
    LLMに送るためのメッセージのリストを作成する関数
    """
    messages = []
    for data in displayed_chat_messages:
        if data['role'] == 'user':
            message = HumanMessage(content=data['content'])
        elif data['role'] == 'assistant':
            message = AIMessage(content=data['content'])
        else:
            raise ValueError(f'role({data["role"]}) is invalid value')
        messages.append(message)
    return messages

def handle_user_input(
    user_input_text: str,
    displayed_chat_messages: list,
    displayed_chat_ref: firestore.DocumentReference,
    chats_ref: firestore.CollectionReference,
    displayed_chat_title: str,
    title_placeholder: st.delta_generator.DeltaGenerator,
):
    """ユーザー入力を処理して、LLMからの応答を表示し、Firestoreに保存します。"""

    # ユーザーの入力を表示
    with st.chat_message("user"):
        st.markdown(user_input_text)

    # 会話の初めのユーザーの入力の場合はタイトルを作成し、Firestoreに保存
    if len(displayed_chat_messages) == 0:
        chat_title_prompt = f"""
        ChatBotとの会話を開始するためにユーザーが入力した文を与えるので、その内容を要約し会話のタイトルを考えてもらいます。
        出力は、会話のタイトルのみにしてください。
        ユーザーの入力文: {user_input_text} """
        displayed_chat_title = llm.invoke(chat_title_prompt).content.strip()
        _, displayed_chat_ref = add_chat(chats_ref, displayed_chat_title)
        st.session_state.displayed_chat_ref = displayed_chat_ref
        st.session_state.displayed_chat_title = displayed_chat_title
        title_placeholder.markdown(f"# {st.session_state.displayed_chat_title}")

    # ユーザーの入力テキストをセッションステートとFirestoreに格納
    user_input_data = {
        "role": "user",
        "content": user_input_text,
        "timestamp": firestore.SERVER_TIMESTAMP,
    }
    displayed_chat_messages.append(user_input_data)
    if displayed_chat_ref:
        add_message(displayed_chat_ref, user_input_data)
    
    # llmの返答をストリーミング出力で表示
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        assistant_output_text = ""
        messages = create_messages(displayed_chat_messages)
        for chunk in stream_graph(messages):
            assistant_output_text += chunk
            message_placeholder.markdown(assistant_output_text)

    # llmの返答をセッションステートとFirestoreに格納
    assistant_output_data = {
        "role": "assistant",
        "content": assistant_output_text,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    displayed_chat_messages.append(assistant_output_data)
    if displayed_chat_ref:
        add_message(displayed_chat_ref, assistant_output_data)
    
    st.session_state.displayed_chat_messages = displayed_chat_messages

