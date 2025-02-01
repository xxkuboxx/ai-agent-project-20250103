from typing import Generator, List
from langchain_core.messages import BaseMessage

from graph.graph_builder import graph


def stream_graph(messages: List[BaseMessage]) -> Generator[str, None, None]:
    inputs = {"messages": messages,  "is_message_output": False, "retry_count": 0}
    streaming = graph.stream(inputs)
    for chunk in streaming:
        if 'mbti_chatbot' in chunk:
            yield chunk["mbti_chatbot"]["messages"][-1].content
        else:
            continue
