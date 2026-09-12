from collections.abc import Iterator

from chain import preparar_entrada_chain, stream_resposta_chain
from config import OLLAMA_AGENT_MODEL, OLLAMA_MODEL


def run_query_stream(pergunta: str) -> Iterator[str]:
    try:
        entrada = preparar_entrada_chain(pergunta)
        yield from stream_resposta_chain(entrada)
    except Exception as exc:
        yield (
            f"Não foi possível processar a pergunta: {exc}\n\n"
            f"Verifique Ollama, {OLLAMA_AGENT_MODEL} e {OLLAMA_MODEL}."
        )


def run_query(pergunta: str) -> str:
    return "".join(run_query_stream(pergunta))
