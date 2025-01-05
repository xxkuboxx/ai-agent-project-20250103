from typing import Annotated, List, Generator
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    message_stream: Generator
