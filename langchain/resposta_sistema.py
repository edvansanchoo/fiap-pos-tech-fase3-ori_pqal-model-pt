import re
from collections.abc import Iterator

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from config import OLLAMA_AGENT_MODEL, OLLAMA_BASE_URL

SISTEMA_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """Você formata respostas sobre dados clínicos do sistema.

Regras:
- Use APENAS os dados fornecidos. Não invente informações.
- Responda em português claro e direto.
- Se for ajuda do sistema, preserve as instruções importantes.
- Se faltar contexto PQAL, explique o formato Pergunta + Contexto.""",
    ),
    (
        "human",
        """DADOS COLETADOS:
{contexto}

PERGUNTA:
{pergunta}""",
    ),
])

_llm_sistema = ChatOllama(
    model=OLLAMA_AGENT_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
)


def _extrair_blocos_dados(contexto: str) -> list[str]:
    blocos = re.findall(r"\*\*Dados:\*\*\n(.*?)(?=\n\n### Tool:|\Z)", contexto, re.DOTALL)
    return [b.strip() for b in blocos if b.strip()]


def _resposta_direta(contexto: str) -> str | None:
    if "PQAL_SEM_CONTEXTO" in contexto:
        for bloco in _extrair_blocos_dados(contexto):
            if "PQAL_SEM_CONTEXTO" in bloco:
                return bloco.replace("PQAL_SEM_CONTEXTO: ", "").strip()
    blocos = _extrair_blocos_dados(contexto)
    if len(blocos) == 1:
        return blocos[0]
    return None


def formatar_resposta_sistema(pergunta: str, contexto: str) -> str:
    direta = _resposta_direta(contexto)
    if direta:
        return direta
    chain = SISTEMA_PROMPT | _llm_sistema | StrOutputParser()
    return chain.invoke({"pergunta": pergunta, "contexto": contexto})


def stream_resposta_sistema(pergunta: str, contexto: str) -> Iterator[str]:
    direta = _resposta_direta(contexto)
    if direta:
        yield direta
        return
    chain = SISTEMA_PROMPT | _llm_sistema | StrOutputParser()
    for chunk in chain.stream({"pergunta": pergunta, "contexto": contexto}):
        if chunk:
            yield chunk
