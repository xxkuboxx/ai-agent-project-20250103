import os

from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm():
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp",
                                  google_api_key=gemini_api_key)


llm = get_llm()
