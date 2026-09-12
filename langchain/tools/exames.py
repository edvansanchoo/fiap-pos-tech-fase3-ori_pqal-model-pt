from langchain_core.tools import tool
from db import queries
from tools.parse_input import parse_int_id, parse_limite
from tools.schemas import BuscarExamesInput


@tool(args_schema=BuscarExamesInput)
def buscar_exames(paciente_id: str, limite: str = "") -> str:
    """Busca os exames mais recentes de um paciente pelo ID numérico."""
    pid = parse_int_id(paciente_id)
    if pid is None:
        return f"ID de paciente inválido: '{paciente_id}'. Use apenas o número do ID."

    lim = parse_limite(limite)
    exames = queries.buscar_exames(pid, limite=lim)
    if not exames:
        return f"Nenhum exame encontrado para o paciente {pid}."

    linhas = []
    for e in exames:
        linhas.append(f"{e['data']} - {e['tipo']}:\n{e['resultado']}")
    return "\n\n".join(linhas)
