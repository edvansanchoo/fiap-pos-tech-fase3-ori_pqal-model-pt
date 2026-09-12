from collections.abc import Iterator
from langchain_ollama import ChatOllama
from config import OLLAMA_BASE_URL, OLLAMA_MODEL


def stream_prompt(prompt: str) -> Iterator[str]:
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )
    for chunk in llm.stream(prompt):
        if chunk.content:
            yield chunk.content
