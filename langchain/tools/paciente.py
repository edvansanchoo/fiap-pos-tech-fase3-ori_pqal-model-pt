from langchain_core.tools import tool
from db import queries
from tools.parse_input import parse_int_id
from tools.schemas import BuscarPacienteInput


@tool(args_schema=BuscarPacienteInput)
def buscar_paciente(nome_ou_id: str) -> str:
    """Busca UM paciente por nome (parcial) ou ID numérico. Para listar todos, use listar_pacientes_disponiveis."""
    nome_ou_id = nome_ou_id.strip().strip('"').strip("'")
    pid = parse_int_id(nome_ou_id)
    if pid is not None and nome_ou_id and nome_ou_id[0].isdigit():
        paciente = queries.buscar_paciente_por_id(pid)
        if not paciente:
            return f"Paciente com ID {pid} não encontrado."
        idade = queries.calcular_idade(paciente["data_nascimento"])
        return f"ID: {paciente['id']}\nNome: {paciente['nome']}\nIdade: {idade} anos"

    resultados = queries.buscar_paciente_por_nome(nome_ou_id)
    if not resultados:
        return f"Nenhum paciente encontrado com nome contendo '{nome_ou_id}'."

    linhas = []
    for p in resultados:
        idade = queries.calcular_idade(p["data_nascimento"])
        linhas.append(f"ID: {p['id']} | Nome: {p['nome']} | Idade: {idade} anos")
    return "\n".join(linhas)
