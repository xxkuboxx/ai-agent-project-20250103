from langchain_core.messages import SystemMessage
from graph.state import State
from pydantic import BaseModel, Field

from graph.llm import llm


class TakeABreak(BaseModel):
    take_a_break: bool = Field(description="会話がひと段落した場合はTrue, そうでない場合はFalse")


SYSTEN_PROMPT = f"""\
あなたは会話がひと段落したかどうか判定する係です。
今までの会話履歴から会話がひと段落したかどうか判定してください。

"Tips: Make sure to answer in the correct format."
"""


def reflector(state: State):
    llm_structured = llm.with_structured_output(TakeABreak)
    messages = state["messages"].copy()
    messages.insert(0, SystemMessage(content=SYSTEN_PROMPT))
    response = llm_structured.with_retry(stop_after_attempt=3).invoke(messages)

    # リトライする場合リトライ回数をカウントアップする。
    retry_count = state["retry_count"]
    if not response.take_a_break:
        retry_count += 1
    
    return {"take_a_break": response.take_a_break,
            "retry_count": retry_count}

