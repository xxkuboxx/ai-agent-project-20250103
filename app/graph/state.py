from typing import Annotated, List, Generator
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    mbti_type: str
    take_a_break: bool
    retry_count: int
    max_retry_count: int
    minutes: str
    chat_memory: int
