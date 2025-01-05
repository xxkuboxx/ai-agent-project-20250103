from langgraph.graph import StateGraph
from langgraph.graph import START, END

from graph.state import State
from graph.nodes.chatbot import chatbot


def create_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile()


graph = create_graph()
