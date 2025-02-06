from langchain_core.messages import SystemMessage
from graph.state import State
from pydantic import BaseModel, Field

from graph.llm import llm


class IsSpeakerUser(BaseModel):
    is_speaker_user: bool = Field(description="次の発言がユーザーに求められている場合はTrue, そうでない場合はFalse")


def generate_system_prompt(user_name):
    """
    system_promptの作成
    """
    # プロンプト作成
    system_prompt = f"""\
あなたは次の発言がユーザー（{user_name}）に求められているのかどうかを予測するエキスパートです。
次の発言がユーザー（{user_name}）に求められているかどうか判定してください。

"Tips: Make sure to answer in the correct format."
"""
    return system_prompt

def reflector(state: State):
    llm_structured = llm.with_structured_output(IsSpeakerUser)
    user_name = state["user_name"]
    chat_memory = state["chat_memory"]
    messages = state["messages"][-chat_memory:].copy()
    messages.insert(0, SystemMessage(content=generate_system_prompt(user_name)))
    response = llm_structured.with_retry(stop_after_attempt=3).invoke(messages)

    # リトライする場合リトライ回数をカウントアップする。
    retry_count = state["retry_count"]
    if not response.is_speaker_user:
        retry_count += 1
    
    return {"is_speaker_user": response.is_speaker_user,
            "retry_count": retry_count}

