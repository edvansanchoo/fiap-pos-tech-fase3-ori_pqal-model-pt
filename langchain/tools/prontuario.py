from langchain_core.tools import tool
from db import queries
from tools.parse_input import parse_int_id, parse_limite
from tools.schemas import BuscarProntuarioInput


@tool(args_schema=BuscarProntuarioInput)
def buscar_prontuario(paciente_id: str, limite: str = "") -> str:
    """Busca entradas recentes do prontuário de um paciente pelo ID numérico."""
    pid = parse_int_id(paciente_id)
    if pid is None:
        return f"ID de paciente inválido: '{paciente_id}'. Use apenas o número do ID."

    lim = parse_limite(limite)
    entradas = queries.buscar_prontuario(pid, limite=lim)
    if not entradas:
        return f"Nenhuma entrada de prontuário encontrada para o paciente {pid}."

    linhas = []
    for e in entradas:
        linhas.append(f"{e['data']}:\n{e['descricao']}")
    return "\n\n".join(linhas)
