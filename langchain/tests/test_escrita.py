from datetime import date

from db import queries
from tools.escrita import atualizar_paciente, criar_paciente, registrar_exame


def test_criar_paciente_tool():
    nome = "Paciente Teste Escrita"
    resultado = criar_paciente.invoke({
        "nome": nome,
        "data_nascimento": "1980-05-15",
    })
    assert "cadastrado com sucesso" in resultado
    encontrados = queries.buscar_paciente_por_nome(nome)
    assert any(p["nome"] == nome for p in encontrados)


def test_atualizar_paciente_tool():
    criado = queries.criar_paciente("Paciente Atualizar", date(1975, 1, 1))
    novo_nome = "Paciente Atualizado Nome"
    resultado = atualizar_paciente.invoke({
        "paciente_id": str(criado["id"]),
        "nome": novo_nome,
        "data_nascimento": "",
    })
    assert "Paciente atualizado" in resultado
    paciente = queries.buscar_paciente_por_id(criado["id"])
    assert paciente["nome"] == novo_nome


def test_registrar_exame_tool():
    criado = queries.criar_paciente("Paciente Exame", date(1990, 6, 10))
    resultado = registrar_exame.invoke({
        "paciente_id": str(criado["id"]),
        "tipo": "Glicemia",
        "resultado": "99 mg/dL",
        "data": "2026-09-12",
    })
    assert "Exame registrado" in resultado
    exames = queries.buscar_exames(criado["id"], limite=1)
    assert exames[0]["resultado"] == "99 mg/dL"
