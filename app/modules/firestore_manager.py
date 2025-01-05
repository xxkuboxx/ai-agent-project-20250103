import streamlit as st
from google.cloud import firestore


def create_user_id(gcp_project: str, local_storage):
    """Firestoreに新しい空ドキュメントを作成し、そのIDをユーザーIDとする。
    ユーザーIDはローカルストレージとセッションステートに保存する。"""
    db = firestore.Client(project=gcp_project)
    doc_ref = db.collection("users").document()
    doc_ref.set({})
    local_storage.setItem("user_id", doc_ref.id)
    st.session_state["user_id"] = doc_ref.id
    st.rerun()

def init_chats_ref(gcp_project: str, user_id: str) -> firestore.CollectionReference:
    """Firestoreのchatsコレクションの参照を初期化します。"""
    db = firestore.Client(project=gcp_project)
    user_ref = db.collection("users").document(user_id)
    return user_ref.collection("chats")

def load_chat_doc(chats_ref: firestore.CollectionReference) -> list:
    """Firestoreからチャットのdocをロードします。"""
    return [doc for doc in chats_ref.order_by("created", direction=firestore.Query.DESCENDING).stream()]

def add_chat(chats_ref: firestore.CollectionReference, title: str) -> tuple[firestore.DocumentReference, firestore.DocumentReference]:
    """Firestoreに新しいチャットを追加します。"""
    return chats_ref.add({
        'title': title,
        'created': firestore.SERVER_TIMESTAMP,
    })

def add_message(chat_ref: firestore.DocumentReference, message_data: dict) -> firestore.DocumentReference:
    """Firestoreにメッセージを追加します。"""
    return chat_ref.collection("messages").add(message_data)

def get_chat_messages(chat_ref: firestore.DocumentReference) -> list:
    """Firestoreからチャットメッセージを取得します。"""
    return [
        msg.to_dict()
        for msg in chat_ref.collection("messages").order_by("timestamp").stream()
    ]

def get_chat(chat_ref: firestore.DocumentReference) -> firestore.DocumentSnapshot:
    """Firestoreからチャットを取得します。"""
    return chat_ref.get()

def delete_document_from_snapshot(doc_snapshot: firestore.DocumentSnapshot):
    """
    DocumentSnapshotからドキュメントを削除する関数
    Args:
        doc_snapshot (firestore.DocumentSnapshot): 削除するドキュメントのスナップショット
    """
    if not doc_snapshot.exists:
      raise ValueError("指定されたドキュメントは存在しません。")
    doc_ref = doc_snapshot.reference  # DocumentReferenceを取得
    try:
        doc_ref.delete()
    except Exception:
        raise RuntimeError(f"ドキュメント {doc_snapshot.id} の削除に失敗しました。")
