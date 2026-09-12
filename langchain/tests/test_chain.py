from agent import GatherResult
from chain import clinical_chain, preparar_entrada_chain


def test_clinical_chain_estrutura():
    assert clinical_chain is not None


def test_preparar_entrada_chain_mock_tools(monkeypatch):
    monkeypatch.setattr(
        "chain.gather_structured_context",
        lambda p: GatherResult(
            contexto="### Tool: listar_pacientes_disponiveis\n**Dados:**\nJoão Silva",
            tools_usadas=["listar_pacientes_disponiveis"],
        ),
    )
    entrada = preparar_entrada_chain("liste os pacientes")
    assert "João Silva" in entrada["contexto"]
    assert entrada["pergunta"] == "liste os pacientes"
    assert entrada["usar_ori_pqal"] is False
    assert entrada["tools_usadas"] == ["listar_pacientes_disponiveis"]
