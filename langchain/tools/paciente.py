from langchain_core.tools import tool
from db import queries


@tool
def buscar_paciente(nome_ou_id: str) -> str:
    """Busca paciente por nome (parcial) ou ID numérico. Retorna dados básicos do paciente."""
    nome_ou_id = nome_ou_id.strip()
    if nome_ou_id.isdigit():
        paciente = queries.buscar_paciente_por_id(int(nome_ou_id))
        if not paciente:
            return f"Paciente com ID {nome_ou_id} não encontrado."
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
