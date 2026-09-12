import re
from dataclasses import dataclass

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from config import OLLAMA_AGENT_MODEL, OLLAMA_BASE_URL

TOOLS_SISTEMA = {
    "listar_pacientes_disponiveis",
    "mostrar_ajuda",
    "buscar_paciente",
    "criar_paciente",
    "atualizar_paciente",
    "buscar_exames",
    "registrar_exame",
    "buscar_medicamentos",
    "registrar_medicamento",
    "buscar_prontuario",
    "montar_contexto_paciente",
}

ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """Classifique se a pergunta deve usar o modelo PQAL especializado (ori-pqal-pt).

Use ori_pqal SOMENTE quando a pergunta é de pesquisa clínica no estilo PQAL:
- pergunta sobre saúde/medicina com contexto científico (artigo, estudo, trecho)
- formato sim/não/talvez com base no contexto fornecido
- similar ao dataset PQAL (Pergunta + Contexto científico)

Use sistema quando:
- consulta pacientes, exames, medicamentos, prontuário deste banco
- listagem de pacientes ou ajuda do sistema
- PQAL sem contexto científico (só explicar formato)

Responda APENAS: ori_pqal ou sistema""",
    ),
    (
        "human",
        """Pergunta:
{pergunta}

Dados coletados:
{contexto}""",
    ),
])

_llm_router = ChatOllama(
    model=OLLAMA_AGENT_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
)


@dataclass
class Roteamento:
    usar_ori_pqal: bool
    motivo: str


MOTIVOS_LEGENDA = {
    "pqal_sem_contexto": "PQAL sem contexto — explicar formato",
    "pqal_com_contexto": "PQAL com contexto científico",
    "contexto_na_pergunta": "contexto científico na pergunta",
}


def legenda_motivo(motivo: str) -> str:
    if motivo in MOTIVOS_LEGENDA:
        return MOTIVOS_LEGENDA[motivo]
    if motivo.startswith("dados_sistema:"):
        tools = motivo.split(":", 1)[1].replace(",", ", ")
        return f"dados do sistema (tools: {tools})"
    if motivo.startswith("llm:"):
        return motivo.split(":", 1)[1]
    return motivo


def _tem_contexto_cientifico(pergunta: str, contexto: str) -> bool:
    if re.search(r"(?i)contexto\s*:", pergunta):
        return True
    return "CONTEXTO DO ESTUDO:" in contexto


def classificar_roteamento(pergunta: str, contexto: str, tools_usadas: list[str]) -> Roteamento:
    tools = set(tools_usadas)
    tools_sistema = tools & TOOLS_SISTEMA

    if "PQAL_SEM_CONTEXTO" in contexto:
        return Roteamento(False, "pqal_sem_contexto")

    if tools_sistema:
        return Roteamento(False, f"dados_sistema:{','.join(sorted(tools_sistema))}")

    if "preparar_contexto_pqal" in tools and _tem_contexto_cientifico(pergunta, contexto):
        return Roteamento(True, "pqal_com_contexto")

    if _tem_contexto_cientifico(pergunta, contexto):
        return Roteamento(True, "contexto_na_pergunta")

    decisao = (
        ROUTER_PROMPT
        | _llm_router
        | StrOutputParser()
    ).invoke({"pergunta": pergunta, "contexto": contexto[:2000]}).strip().lower()

    if "ori_pqal" in decisao or "ori-pqal" in decisao:
        return Roteamento(True, "llm:ori_pqal")
    return Roteamento(False, "llm:sistema")
