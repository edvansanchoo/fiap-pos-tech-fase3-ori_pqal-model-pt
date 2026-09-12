from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from db import queries

SYSTEM_PROMPT = """Você é um assistente de análise de informações clínicas.
Utilize exclusivamente os dados fornecidos no contexto.
Não invente informações.
Não utilize conhecimento externo para preencher informações ausentes."""


def _montar_contexto(paciente_id: int) -> str:
    paciente = queries.buscar_paciente_por_id(paciente_id)
    if not paciente:
        return ""

    idade = queries.calcular_idade(paciente["data_nascimento"])
    consulta = queries.buscar_ultima_consulta(paciente_id)
    meds = queries.buscar_medicamentos_ativos(paciente_id)
    exames = queries.buscar_exames(paciente_id, limite=1)

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

    if meds:
        linhas.extend(["", "Medicamentos:"])
        for m in meds:
            linhas.append(f"{m['medicamento']} - {m['dose']}")

    if exames:
        ultimo = exames[0]
        linhas.extend([
            "",
            "Último exame:",
            f"{ultimo['tipo']}: {ultimo['resultado']}",
        ])

    return "\n".join(linhas)


@tool
def analisar_paciente(paciente_id: int) -> str:
    """Agrega todos os dados clínicos do paciente e gera uma análise do estado atual."""
    contexto = _montar_contexto(paciente_id)
    if not contexto:
        return f"Paciente {paciente_id} não encontrado."

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    prompt = f"""{SYSTEM_PROMPT}

CONTEXTO:
{contexto}

PERGUNTA:
Faça uma análise do estado atual do paciente."""

    response = llm.invoke(prompt)
    return response.content
