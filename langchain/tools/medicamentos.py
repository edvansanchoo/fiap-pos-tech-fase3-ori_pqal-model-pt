from langchain_core.tools import tool
from db import queries
from tools.parse_input import parse_int_id
from tools.schemas import PacienteIdInput


@tool(args_schema=PacienteIdInput)
def buscar_medicamentos(paciente_id: str) -> str:
    """Busca medicamentos ativos de um paciente pelo ID numérico."""
    pid = parse_int_id(paciente_id)
    if pid is None:
        return f"ID de paciente inválido: '{paciente_id}'. Use apenas o número do ID."

    meds = queries.buscar_medicamentos_ativos(pid)
    if not meds:
        return f"Nenhum medicamento ativo encontrado para o paciente {pid}."

    linhas = []
    for m in meds:
        linhas.append(f"{m['medicamento']} - {m['dose']} (desde {m['data_inicio']})")
    return "\n".join(linhas)
