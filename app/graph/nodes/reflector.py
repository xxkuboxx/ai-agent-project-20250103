from langchain_core.messages import SystemMessage
from graph.state import State
from pydantic import BaseModel, Field

from graph.llm import llm


class TakeABreak(BaseModel):
    take_a_break: bool = Field(description="**網羅性、正確性、構造性、可読性、実用性**の全てを満たす最高品質の議事録を作成できる場合はTrue, そうでない場合はFalse")


SYSTEN_PROMPT = f"""\
あなたは議論がされつくされたかどうかを判定するエキスパートです。
今までの会話履歴を元に、**網羅性、正確性、構造性、可読性、実用性**の全てを満たす最高品質の議事録を作成できるかどうか判定してください。

"Tips: Make sure to answer in the correct format."
"""


def reflector(state: State):
    llm_structured = llm.with_structured_output(TakeABreak)
    chat_memory = state["chat_memory"]
    messages = state["messages"][-chat_memory:].copy()
    messages.insert(0, SystemMessage(content=SYSTEN_PROMPT))
    response = llm_structured.with_retry(stop_after_attempt=3).invoke(messages)

    # リトライする場合リトライ回数をカウントアップする。
    retry_count = state["retry_count"]
    if not response.take_a_break:
        retry_count += 1
    
    return {"take_a_break": response.take_a_break,
            "retry_count": retry_count}

