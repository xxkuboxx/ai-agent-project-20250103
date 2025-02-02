import os

import streamlit as st
from streamlit_local_storage import LocalStorage
from dotenv import load_dotenv
load_dotenv()

from modules.chat_manager import handle_user_input, create_messages
from modules.firestore_manager import create_user_id, fetch_chats_ref
from modules.sidebar_manager import display_sidebar
from modules.create_minutes import create_minutes


GCP_PROJECT = os.environ["GCP_PROJECT"]
NEW_CHAT_TITLE = "New Chat"


def main():
    # Initialize session state
    if "user_id" not in st.session_state:
        # ローカルストレージにuser_idがある場合は、セッションステートに格納する。
        # ない場合は新たに作成し、ローカルストレージとセッションステートに格納する。
        local_storage = LocalStorage()
        user_id = local_storage.getItem("user_id")
        if user_id:
            st.session_state["user_id"] = user_id
        else:
            user_id = create_user_id()
            local_storage.setItem("user_id", user_id)
            st.session_state["user_id"] = user_id

    if "chats_ref" not in st.session_state:
        st.session_state.chats_ref = fetch_chats_ref(st.session_state.user_id)

    if "displayed_chat_ref" not in st.session_state:
        st.session_state.displayed_chat_ref = None

    if "displayed_chat_title" not in st.session_state:
        st.session_state.displayed_chat_title = NEW_CHAT_TITLE

    if "displayed_chat_messages" not in st.session_state:
        st.session_state.displayed_chat_messages = []

    if "minutes_button_clicked" not in st.session_state:
        st.session_state.minutes_button_clicked = False

    if "user_name" not in st.session_state:
        st.session_state.user_name = "ユーザー"

    # Sidebar
    with st.sidebar:
        st.session_state.user_name = st.text_input("ユーザー名",  value=st.session_state.user_name)
        max_retry_count = st.number_input(
            "最大自動会話回数",
            min_value=1, max_value=20,
            value=3, step=1)
        if st.button("議事録作成"):
            st.session_state.minutes_button_clicked = True
        display_sidebar(
            st.session_state.chats_ref,
            NEW_CHAT_TITLE,
        )

    
    # タイトルとメッセージの表示
    title_placeholder = st.empty()
    title_placeholder.markdown(f"# {st.session_state.displayed_chat_title}")
    for message in st.session_state.displayed_chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_input_text = st.chat_input("質問を入力してください")
    if user_input_text:
        user_input_text = f"{st.session_state.user_name}: {user_input_text}"
        st.session_state.minutes = handle_user_input(
            user_input_text,
            st.session_state.displayed_chat_messages,
            st.session_state.displayed_chat_ref,
            st.session_state.chats_ref,
            st.session_state.displayed_chat_title,
            title_placeholder,
            max_retry_count,
        )

    if st.session_state.minutes_button_clicked:
        # 議事録作成
        messages = create_messages(st.session_state.displayed_chat_messages)
        minutes = create_minutes(messages)
        st.markdown(minutes)
        st.session_state.minutes_button_clicked = False # ボタンが押された状態をリセット（必要な場合）

if __name__ == '__main__':
    main()
