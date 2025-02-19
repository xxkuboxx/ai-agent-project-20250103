from typing import Generator, List
from langchain_core.messages import BaseMessage

from graph.graph_builder import graph


def stream_graph(messages: List[BaseMessage], max_retry_count: int, user_name: str) -> Generator[str, None, None]:
    inputs = {"messages": messages,
              "retry_count": 0,
              "max_retry_count": max_retry_count,
              "chat_memory": 10,
              "user_name": user_name}
    streaming = graph.stream(inputs, {"recursion_limit": 50})
    for chunk in streaming:
        if 'mbti_chatbot' in chunk:
            yield chunk["mbti_chatbot"]["messages"][-1].content, chunk["mbti_chatbot"]["search_web_list"],
        else:
            continue
