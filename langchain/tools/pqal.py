import re
from langchain_core.tools import tool
from tools.schemas import TextoInput


def _normalizar_texto_pqal(texto: str) -> str:
    texto = texto.strip().strip('"').strip("'")
    texto = re.sub(r"\\n", "\n", texto)
    texto = re.sub(r"\\t", "\t", texto)
    return texto


def _extrair_pergunta_e_contexto(texto: str) -> tuple[str, str]:
    texto = _normalizar_texto_pqal(texto)
    ctx_match = re.search(r"(?i)contexto\s*:\s*", texto)
    if ctx_match:
        pergunta_part = texto[: ctx_match.start()].strip()
        contexto = texto[ctx_match.end() :].strip()
        pergunta_part = re.sub(r"^pergunta\s*:\s*", "", pergunta_part, flags=re.IGNORECASE).strip()
        return pergunta_part, contexto
    return texto, ""


def tem_contexto_pqal(texto: str) -> bool:
    _, contexto = _extrair_pergunta_e_contexto(texto)
    return bool(contexto)


def formatar_contexto_pqal(texto: str) -> str:
    pergunta, contexto = _extrair_pergunta_e_contexto(texto)
    if not contexto:
        return (
            "PQAL_SEM_CONTEXTO: o usuário precisa enviar Pergunta e Contexto no formato "
            "Pergunta: ... Contexto: ..."
        )
    return f"PERGUNTA PQAL:\n{pergunta}\n\nCONTEXTO DO ESTUDO:\n{contexto}"


@tool(args_schema=TextoInput)
def preparar_contexto_pqal(texto: str) -> str:
    """Use para perguntas PQAL (sim/não/talvez). Passe a mensagem COMPLETA do usuário, sem resumir."""
    return formatar_contexto_pqal(texto)
