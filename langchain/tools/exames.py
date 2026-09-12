from langchain_core.tools import tool
from db import queries


@tool
def buscar_exames(paciente_id: int, limite: int = 5) -> str:
    """Busca os exames mais recentes de um paciente pelo ID."""
    exames = queries.buscar_exames(paciente_id, limite=limite)
    if not exames:
        return f"Nenhum exame encontrado para o paciente {paciente_id}."

    linhas = []
    for e in exames:
        linhas.append(f"{e['data']} - {e['tipo']}:\n{e['resultado']}")
    return "\n\n".join(linhas)
