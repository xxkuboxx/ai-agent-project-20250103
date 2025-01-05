from typing import Generator, List
from langchain_core.messages import BaseMessage

from graph.graph_builder import graph


def stream_graph(messages: List[BaseMessage]) -> Generator[str, None, None]:
    inputs = {"messages": messages}
    output = graph.invoke(inputs)
    for chunk in output['message_stream']:
        yield  chunk.content
