from ui_progress import montar_texto_tools


def test_montar_texto_tools_vazio():
    assert montar_texto_tools([], []) == "_Aguardando agente..._"


def test_montar_texto_tools_com_linhas():
    texto = montar_texto_tools(
        ["⏳ Executando `buscar_paciente`"],
        ["buscar_paciente"],
    )
    assert "buscar_paciente" in texto
    assert "Concluídas" in texto
