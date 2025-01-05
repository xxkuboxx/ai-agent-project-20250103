import os

from langchain_google_vertexai import ChatVertexAI

def get_llm():
    gcp_project = os.getenv("GCP_PROJECT")
    return ChatVertexAI(model="gemini-2.0-flash-exp",
                        project=gcp_project)


llm = get_llm()
