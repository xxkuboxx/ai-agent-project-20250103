from typing import Generator, List
from langchain_core.messages import BaseMessage

from graph.graph_builder import graph


def stream_graph(messages: List[BaseMessage]) -> Generator[str, None, None]:
    inputs = {"messages": messages,
              "retry_count": 0,
              "max_retry_count": 10,
              "chat_memory": 10}
    streaming = graph.stream(inputs, {"recursion_limit": 50})
    for chunk in streaming:
        if 'mbti_chatbot' in chunk:
            type = "message"
            yield type, chunk["mbti_chatbot"]["messages"][-1].content
        elif 'reporter' in chunk:
            type = "minutes"
            yield type, chunk["reporter"]["minutes"]
        else:
            continue
