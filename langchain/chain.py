from collections.abc import Iterator

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama

from agent import gather_structured_context
from config import OLLAMA_AGENT_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL
from llm_stream import stream_prompt
from resposta_sistema import formatar_resposta_sistema, stream_resposta_sistema
from router import classificar_roteamento, legenda_motivo

ORI_SYSTEM = """Com base no contexto científico fornecido, responda à pergunta com sim, não ou talvez e justifique brevemente.

Regras:
- Use APENAS o contexto científico fornecido.
- Não invente informações.
- Formato: Resposta: sim/não/talvez seguido de justificativa breve."""

ORI_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ORI_SYSTEM),
    (
        "human",
        """DADOS ESTRUTURADOS COLETADOS:
{contexto}

PERGUNTA DO USUÁRIO:
{pergunta}""",
    ),
])

_llm_resposta = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
)

def preparar_entrada_chain(pergunta: str) -> dict:
    """Executa etapas 1 e 2: coleta via agente + roteamento."""
    coleta = gather_structured_context(pergunta)
    roteamento = classificar_roteamento(
        pergunta,
        coleta.contexto,
        coleta.tools_usadas,
    )
    usar_ori = roteamento.usar_ori_pqal
    return {
        "pergunta": pergunta,
        "contexto": coleta.contexto,
        "tools_usadas": coleta.tools_usadas,
        "usar_ori_pqal": usar_ori,
        "motivo_roteamento": roteamento.motivo,
        "modelo_resposta": OLLAMA_MODEL if usar_ori else OLLAMA_AGENT_MODEL,
        "motivo_legenda": legenda_motivo(roteamento.motivo),
    }


def _montar_prompt_texto(entrada: dict) -> str:
    messages = ORI_PROMPT.format_messages(
        contexto=entrada["contexto"],
        pergunta=entrada["pergunta"],
    )
    partes = []
    for msg in messages:
        role = "SYSTEM" if msg.type == "system" else "USER"
        partes.append(f"{role}:\n{msg.content}")
    return "\n\n".join(partes)


def _responder_com_ori_pqal(entrada: dict) -> str:
    return (ORI_PROMPT | _llm_resposta | StrOutputParser()).invoke(entrada)


def stream_resposta_chain(entrada: dict) -> Iterator[str]:
    """Etapa 3: stream da resposta final."""
    if entrada["usar_ori_pqal"]:
        yield from stream_prompt(_montar_prompt_texto(entrada))
    else:
        yield from stream_resposta_sistema(entrada["pergunta"], entrada["contexto"])


def run_clinical_chain(pergunta: str) -> str:
    entrada = preparar_entrada_chain(pergunta)
    if entrada["usar_ori_pqal"]:
        return _responder_com_ori_pqal(entrada)
    return formatar_resposta_sistema(entrada["pergunta"], entrada["contexto"])


def run_clinical_chain_stream(pergunta: str) -> Iterator[str]:
    entrada = preparar_entrada_chain(pergunta)
    yield from stream_resposta_chain(entrada)


clinical_chain = RunnableLambda(run_clinical_chain)
