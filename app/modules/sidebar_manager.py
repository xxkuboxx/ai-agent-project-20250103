import streamlit as st
from google.cloud import firestore

from modules.firestore_manager import get_chat_messages, load_chat_doc, delete_document_from_snapshot


def create_new_chat(new_chat_title):
    """新しいチャットを作成します。"""
    st.session_state.displayed_chat_title = new_chat_title
    st.session_state.displayed_chat_messages = []
    st.session_state.minutes = ""


def change_displayed_chat(chat_doc: firestore.DocumentSnapshot):
    """表示するチャットを切り替えます。"""
    st.session_state.displayed_chat_ref = chat_doc.reference
    st.session_state.displayed_chat_title = chat_doc.to_dict()["title"]
    st.session_state.displayed_chat_messages = get_chat_messages(chat_doc.reference)
    st.session_state.minutes = ""

def delete_chat(chat_doc: firestore.DocumentSnapshot):
    """チャット履歴を削除する関数"""
    delete_document_from_snapshot(chat_doc)

def display_sidebar(
    chats_ref: firestore.CollectionReference,
    displayed_chat_title: str,
    new_chat_title: str,
):
    """サイドバーを表示します。"""
    new_chat_disabled = displayed_chat_title == new_chat_title
    st.button("新しい会話を始める", on_click=create_new_chat,  args=(new_chat_title,), type="primary")
    st.title("過去の会話履歴")
    for i, doc in enumerate(load_chat_doc(chats_ref)):
        data = doc.to_dict()
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.button(
                    data["title"], on_click=change_displayed_chat, args=(doc,), key=f"chat_button_{i}"
                )
            with col2:
                st.button(
                    "削除", on_click=delete_chat, args=(doc,), key=f"delete_button_{i}", type="tertiary"
                )

