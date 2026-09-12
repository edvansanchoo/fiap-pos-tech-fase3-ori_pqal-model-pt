from langchain_core.tools import tool
from db import queries
from tools.parse_input import parse_data, parse_int_id
from tools.schemas import (
    AtualizarPacienteInput,
    CriarPacienteInput,
    RegistrarExameInput,
    RegistrarMedicamentoInput,
)


@tool(args_schema=CriarPacienteInput)
def criar_paciente(nome: str, data_nascimento: str) -> str:
    """Cadastra um novo paciente no banco. Informe nome e data de nascimento."""
    nascimento = parse_data(data_nascimento)
    if not nome.strip():
        return "Nome do paciente é obrigatório."
    if nascimento is None:
        return f"Data de nascimento inválida: '{data_nascimento}'. Use YYYY-MM-DD ou DD/MM/YYYY."

    paciente = queries.criar_paciente(nome.strip(), nascimento)
    idade = queries.calcular_idade(paciente["data_nascimento"])
    return (
        f"Paciente cadastrado com sucesso.\n"
        f"ID: {paciente['id']}\n"
        f"Nome: {paciente['nome']}\n"
        f"Idade: {idade} anos"
    )


@tool(args_schema=AtualizarPacienteInput)
def atualizar_paciente(
    paciente_id: str,
    nome: str = "",
    data_nascimento: str = "",
) -> str:
    """Atualiza nome ou data de nascimento de um paciente existente pelo ID."""
    pid = parse_int_id(paciente_id)
    if pid is None:
        return f"ID de paciente inválido: '{paciente_id}'."

    novo_nome = nome.strip() if nome and nome.strip() else None
    nova_data = parse_data(data_nascimento) if data_nascimento and data_nascimento.strip() else None

    if novo_nome is None and nova_data is None:
        return "Informe pelo menos um campo para atualizar: nome ou data_nascimento."
    if data_nascimento and data_nascimento.strip() and nova_data is None:
        return f"Data de nascimento inválida: '{data_nascimento}'."

    paciente = queries.atualizar_paciente(pid, nome=novo_nome, data_nascimento=nova_data)
    if not paciente:
        return f"Paciente com ID {pid} não encontrado."

    idade = queries.calcular_idade(paciente["data_nascimento"])
    return (
        f"Paciente atualizado.\n"
        f"ID: {paciente['id']}\n"
        f"Nome: {paciente['nome']}\n"
        f"Idade: {idade} anos"
    )


@tool(args_schema=RegistrarExameInput)
def registrar_exame(
    paciente_id: str,
    tipo: str,
    resultado: str,
    data: str = "",
) -> str:
    """Registra um novo exame para um paciente pelo ID."""
    pid = parse_int_id(paciente_id)
    if pid is None:
        return f"ID de paciente inválido: '{paciente_id}'."
    if not queries.buscar_paciente_por_id(pid):
        return f"Paciente com ID {pid} não encontrado."

    data_exame = parse_data(data) if data and data.strip() else None
    if data and data.strip() and data_exame is None:
        return f"Data do exame inválida: '{data}'."

    exame = queries.registrar_exame(pid, tipo, resultado, data_exame)
    return (
        f"Exame registrado para paciente {pid}.\n"
        f"{exame['data']} - {exame['tipo']}: {exame['resultado']}"
    )


@tool(args_schema=RegistrarMedicamentoInput)
def registrar_medicamento(
    paciente_id: str,
    medicamento: str,
    dose: str,
    data_inicio: str = "",
) -> str:
    """Registra um medicamento ativo para um paciente pelo ID."""
    pid = parse_int_id(paciente_id)
    if pid is None:
        return f"ID de paciente inválido: '{paciente_id}'."
    if not queries.buscar_paciente_por_id(pid):
        return f"Paciente com ID {pid} não encontrado."

    inicio = parse_data(data_inicio) if data_inicio and data_inicio.strip() else None
    if data_inicio and data_inicio.strip() and inicio is None:
        return f"Data de início inválida: '{data_inicio}'."

    med = queries.registrar_medicamento(pid, medicamento, dose, inicio)
    return (
        f"Medicamento registrado para paciente {pid}.\n"
        f"{med['medicamento']} - {med['dose']} (desde {med['data_inicio']})"
    )
