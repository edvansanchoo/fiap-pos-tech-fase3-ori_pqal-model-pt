from datetime import date
from db import queries


def test_buscar_paciente_por_id_encontra_joao():
    paciente = queries.buscar_paciente_por_id(1)
    assert paciente is not None
    assert paciente["nome"] == "João Silva"


def test_buscar_paciente_por_nome_encontra_joao():
    resultados = queries.buscar_paciente_por_nome("joão")
    assert len(resultados) >= 1
    assert resultados[0]["nome"] == "João Silva"


def test_buscar_exames_retorna_glicemia():
    exames = queries.buscar_exames(1, limite=3)
    assert len(exames) >= 1
    assert any("Glicemia" in e["tipo"] for e in exames)


def test_buscar_medicamentos_ativos_retorna_medicamento_a():
    meds = queries.buscar_medicamentos_ativos(1)
    assert any(m["medicamento"] == "Medicamento A" for m in meds)
    assert all(m["data_fim"] is None for m in meds)


def test_buscar_ultima_consulta_joao():
    consulta = queries.buscar_ultima_consulta(1)
    assert consulta is not None
    assert consulta["pressao_sistolica"] == 145
    assert consulta["pressao_diastolica"] == 90


def test_calcular_idade():
    idade = queries.calcular_idade(date(1958, 3, 15))
    assert idade == 68
