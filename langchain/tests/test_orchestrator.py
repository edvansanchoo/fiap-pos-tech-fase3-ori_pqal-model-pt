from orchestrator import run_query


def test_exames_do_joao():
    resultado = run_query("Quais foram os últimos exames do paciente João?")
    assert "Glicemia" in resultado
    assert "2022" not in resultado


def test_medicamentos_paciente_1():
    resultado = run_query("Quais medicamentos o paciente 1 está tomando?")
    assert "Medicamento A" in resultado


def test_listar_pacientes():
    resultado = run_query("quais os pacientes disponiveis")
    assert "João Silva" in resultado
    assert "Maria Santos" in resultado
    assert "Nenhum paciente encontrado" not in resultado


def test_listar_pacientes_com_typo():
    resultado = run_query("liste os pascientes")
    assert "João Silva" in resultado
    assert "Nenhum paciente encontrado" not in resultado


def test_ajuda():
    resultado = run_query("ajuda")
    assert "PQAL" in resultado
    assert "banco" in resultado.lower()


def test_pqal_sem_contexto_explica_formato():
    resultado = run_query(
        "Terapia de falta de ar controlada pelo paciente em cuidados paliativos?"
    )
    assert "Contexto" in resultado
    assert "Nenhum paciente encontrado" not in resultado
