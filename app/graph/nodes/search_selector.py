from langchain_core.messages import SystemMessage
from graph.state import State
from pydantic import BaseModel, Field

from graph.llm import llm


class IsWebSearch(BaseModel):
    is_web_search: bool = Field(description="Web検索が必要であるかどうかの判定結果。必要である場合はTrue、必要でない場合はFalseとなる。")


SYSTEN_PROMPT = f"""\
次の会話履歴の課題を解決するためにWeb検索が必要であるかどうか判定してください。
Web検索が必要である場合True, Web検索が必要ない場合はFalseを返してください。
判定結果以外は出力しないでください。

"Tips: Make sure to answer in the correct format."
"""


def search_selector(state: State):
    llm_structured = llm.with_structured_output(IsWebSearch)
    chat_memory = state["chat_memory"]
    messages = state["messages"][-chat_memory:].copy()
    messages.insert(0, SystemMessage(content=SYSTEN_PROMPT))
    response = llm_structured.with_retry(stop_after_attempt=5).invoke(messages)
    is_web_search = response.is_web_search
    return {"is_web_search": is_web_search}
