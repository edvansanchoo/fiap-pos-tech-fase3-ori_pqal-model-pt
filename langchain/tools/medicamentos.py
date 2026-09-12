from langchain_core.tools import tool
from db import queries


@tool
def buscar_medicamentos(paciente_id: int) -> str:
    """Busca medicamentos ativos de um paciente pelo ID."""
    meds = queries.buscar_medicamentos_ativos(paciente_id)
    if not meds:
        return f"Nenhum medicamento ativo encontrado para o paciente {paciente_id}."

    linhas = []
    for m in meds:
        linhas.append(f"{m['medicamento']} - {m['dose']} (desde {m['data_inicio']})")
    return "\n".join(linhas)
