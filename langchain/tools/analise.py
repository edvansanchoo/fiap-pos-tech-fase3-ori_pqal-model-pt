from langchain_core.tools import tool
from db import queries
from tools.parse_input import parse_int_id
from tools.schemas import PacienteIdInput


def montar_contexto_paciente_dados(paciente_id: int) -> str:
    paciente = queries.buscar_paciente_por_id(paciente_id)
    if not paciente:
        return ""

    idade = queries.calcular_idade(paciente["data_nascimento"])
    consulta = queries.buscar_ultima_consulta(paciente_id)
    meds = queries.buscar_medicamentos_ativos(paciente_id)
    exames = queries.buscar_exames(paciente_id, limite=5)
    prontuario = queries.buscar_prontuario(paciente_id, limite=3)

    linhas = [
        "CONTEXTO ATUAL DO PACIENTE",
        "",
        f"Paciente: {paciente['nome']}",
        f"Idade: {idade}",
    ]

    if consulta:
        data_fmt = consulta["data"].strftime("%d/%m/%Y")
        linhas.extend(["", "Última consulta:", data_fmt])
        if consulta["pressao_sistolica"] and consulta["pressao_diastolica"]:
            linhas.extend([
                "",
                "Pressão:",
                f"{consulta['pressao_sistolica']}/{consulta['pressao_diastolica']}",
            ])
        if consulta.get("observacoes"):
            linhas.extend(["", "Observações:", consulta["observacoes"]])

    if meds:
        linhas.extend(["", "Medicamentos ativos:"])
        for m in meds:
            linhas.append(f"- {m['medicamento']} {m['dose']} (desde {m['data_inicio']})")

    if exames:
        linhas.extend(["", "Exames recentes:"])
        for e in exames:
            linhas.append(f"- {e['data']} | {e['tipo']}: {e['resultado']}")

    if prontuario:
        linhas.extend(["", "Prontuário recente:"])
        for p in prontuario:
            linhas.append(f"- {p['data']}: {p['descricao']}")

    return "\n".join(linhas)


@tool(args_schema=PacienteIdInput)
def montar_contexto_paciente(paciente_id: str) -> str:
    """Agrega todos os dados clínicos estruturados de um paciente pelo ID."""
    pid = parse_int_id(paciente_id)
    if pid is None:
        return f"ID de paciente inválido: '{paciente_id}'. Use apenas o número do ID."
    contexto = montar_contexto_paciente_dados(pid)
    if not contexto:
        return f"Paciente {pid} não encontrado."
    return contexto
