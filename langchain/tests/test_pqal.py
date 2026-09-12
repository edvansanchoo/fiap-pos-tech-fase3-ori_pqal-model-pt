from tools.pqal import formatar_contexto_pqal, tem_contexto_pqal
from agent import _coletar_pqal_direto


def test_pqal_com_contexto_multilinha():
    texto = (
        "Pergunta: Terapia de falta de ar controlada pelo paciente?\n\n"
        "Contexto: A falta de ar é um dos sintomas mais angustiantes."
    )
    assert tem_contexto_pqal(texto)
    resultado = formatar_contexto_pqal(texto)
    assert "CONTEXTO DO ESTUDO:" in resultado
    assert "falta de ar" in resultado
    assert "PQAL_SEM_CONTEXTO" not in resultado


def test_pqal_com_contexto_literal_newline():
    texto = (
        "Pergunta: Terapia de falta de ar controlada pelo paciente em cuidados paliativos? "
        "Contexto:\\nA falta de ar é um dos sintomas mais angustiantes."
    )
    assert tem_contexto_pqal(texto)
    resultado = formatar_contexto_pqal(texto)
    assert "CONTEXTO DO ESTUDO:" in resultado
    assert "angustiantes" in resultado


def test_coletar_pqal_direto():
    pergunta = (
        "Pergunta: Terapia de falta de ar?\n\n"
        "Contexto: Estudo sobre opióides em cuidados paliativos."
    )
    coleta = _coletar_pqal_direto(pergunta)
    assert coleta is not None
    assert coleta.tools_usadas == ["preparar_contexto_pqal"]
    assert "CONTEXTO DO ESTUDO:" in coleta.contexto


def test_pqal_sem_contexto():
    texto = "Terapia de falta de ar controlada pelo paciente?"
    assert not tem_contexto_pqal(texto)
    assert "PQAL_SEM_CONTEXTO" in formatar_contexto_pqal(texto)
