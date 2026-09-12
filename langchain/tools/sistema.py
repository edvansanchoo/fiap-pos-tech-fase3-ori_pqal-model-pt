from langchain_core.tools import tool
from messages import MENSAGEM_AJUDA, formatar_lista_pacientes


@tool
def listar_pacientes_disponiveis() -> str:
    """Lista todos os pacientes cadastrados no banco de dados."""
    return formatar_lista_pacientes()


@tool
def mostrar_ajuda() -> str:
    """Explica o que o assistente pode fazer e como formular perguntas."""
    return MENSAGEM_AJUDA
