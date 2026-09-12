from tools.paciente import buscar_paciente
from tools.exames import buscar_exames
from tools.medicamentos import buscar_medicamentos


def test_buscar_paciente_tool_por_nome():
    resultado = buscar_paciente.invoke({"nome_ou_id": "João"})
    assert "João Silva" in resultado
    assert "ID: 1" in resultado


def test_buscar_exames_tool():
    resultado = buscar_exames.invoke({"paciente_id": 1, "limite": 3})
    assert "Glicemia" in resultado


def test_buscar_medicamentos_tool():
    resultado = buscar_medicamentos.invoke({"paciente_id": 1})
    assert "Medicamento A" in resultado
