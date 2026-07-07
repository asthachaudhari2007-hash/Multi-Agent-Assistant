import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

load_dotenv()


def get_llm(provider="Gemini"):

    if provider == "Gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.3,
        )

    elif provider == "Ollama":
        return ChatOllama(
            model="llama3.2",
            temperature=0.3,
        )

    else:
        raise ValueError("Invalid model selected")