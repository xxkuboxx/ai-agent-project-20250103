from typing import Annotated, List
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from google.genai.types import GroundingChunk


class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    mbti_type: str
    is_speaker_user: bool
    retry_count: int
    max_retry_count: int
    chat_memory: int
    user_name: str
    is_web_search: bool
    search_result_text: str
    search_web_list: list[GroundingChunk]
