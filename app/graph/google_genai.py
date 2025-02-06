
from google import genai
from google.genai import types


def messages_to_contents(messages):
    contents = []
    for message in messages:
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=message.content)])
        contents.append(content)
    return contents


client = genai.Client(vertexai=True, location='us-central1')
tools = [types.Tool(google_search=types.GoogleSearch())]
generate_content_config = types.GenerateContentConfig(tools = tools)

