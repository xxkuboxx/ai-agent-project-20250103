import os

import streamlit as st
from streamlit_local_storage import LocalStorage
from dotenv import load_dotenv
load_dotenv()

from modules.chat_manager import handle_user_input
from modules.firestore_manager import create_user_id, fetch_chats_ref
from modules.sidebar_manager import display_sidebar


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

    if "minutes" not in st.session_state:
        st.session_state.minutes = ""

    # Sidebar
    with st.sidebar:
        display_sidebar(
            st.session_state.chats_ref,
            st.session_state.displayed_chat_title,
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
        user_input_text = f"ユーザー: {user_input_text}"
        st.session_state.minutes = handle_user_input(
            user_input_text,
            st.session_state.displayed_chat_messages,
            st.session_state.displayed_chat_ref,
            st.session_state.chats_ref,
            st.session_state.displayed_chat_title,
            title_placeholder,
        )
    
    # 議事録の表示
    st.markdown(st.session_state.minutes)

if __name__ == '__main__':
    main()
