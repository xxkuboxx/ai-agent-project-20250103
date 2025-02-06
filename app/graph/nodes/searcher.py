from langchain_core.messages import SystemMessage
from graph.state import State

from graph.google_genai import client, generate_content_config, messages_to_contents



SYSTEN_PROMPT = f"""\
次の会話履歴の課題の解決策をWeb検索してその結果をレポートしてください。
レポートのみ出力し、それ以外は出力しないでください。
必ず日本のWebサイトから情報を持ってきてください。
"""


def searcher(state: State):
    chat_memory = state["chat_memory"]
    messages = state["messages"][-chat_memory:].copy()
    messages.insert(0, SystemMessage(content=SYSTEN_PROMPT))
    response = client.models.generate_content(
        model = "gemini-2.0-flash-001",
        contents = messages_to_contents(messages),
        config = generate_content_config)
    search_result_text = response.candidates[0].content.parts[0].text
    if response.candidates[0].grounding_metadata.grounding_chunks:
        search_web_list = [ grounding_chunk.web for grounding_chunk in response.candidates[0].grounding_metadata.grounding_chunks ]
    else:
        search_web_list = []
    return {"search_result_text": search_result_text,
            "search_web_list": search_web_list}

