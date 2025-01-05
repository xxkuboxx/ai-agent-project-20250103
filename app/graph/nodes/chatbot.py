from graph.state import State

from graph.llm import llm


def chatbot(state: State):
    message_stream = llm.with_retry(stop_after_attempt=3).stream(state["messages"])
    return {"message_stream": message_stream}

