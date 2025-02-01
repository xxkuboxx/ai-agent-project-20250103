from langgraph.graph import StateGraph
from langgraph.graph import START, END

from graph.state import State
from graph.nodes.mbit_chatbot import mbti_chatbot
from graph.nodes.facilitator import facilitator
from graph.nodes.reflector import reflector


def should_retry(state: State) -> str:
    if (state["take_a_break"] or state["retry_count"] >= 3):
        return "finish"
    else:
        return "retry"

def create_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("facilitator", facilitator)
    graph_builder.add_node("mbti_chatbot", mbti_chatbot)
    graph_builder.add_node("reflector", reflector)
    graph_builder.add_edge(START, "facilitator")
    graph_builder.add_edge("facilitator", "mbti_chatbot")
    graph_builder.add_edge("mbti_chatbot", "reflector")
    graph_builder.add_conditional_edges("reflector", should_retry,
                                        {"retry": "facilitator", 
                                         "finish": END})
    return graph_builder.compile()


graph = create_graph()
