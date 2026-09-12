from langchain_core.tools import tool
from db import queries


@tool
def buscar_prontuario(paciente_id: int, limite: int = 5) -> str:
    """Busca entradas recentes do prontuário de um paciente pelo ID."""
    entradas = queries.buscar_prontuario(paciente_id, limite=limite)
    if not entradas:
        return f"Nenhuma entrada de prontuário encontrada para o paciente {paciente_id}."

    linhas = []
    for e in entradas:
        linhas.append(f"{e['data']}:\n{e['descricao']}")
    return "\n\n".join(linhas)
