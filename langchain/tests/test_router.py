from router import classificar_roteamento


def test_roteamento_dados_sistema_listar_pacientes():
    ctx = "### Tool: listar_pacientes_disponiveis\n**Dados:**\nJoão Silva"
    rota = classificar_roteamento("liste os pacientes", ctx, ["listar_pacientes_disponiveis"])
    assert rota.usar_ori_pqal is False


def test_roteamento_pqal_com_contexto():
    ctx = (
        "### Tool: preparar_contexto_pqal\n**Dados:**\n"
        "PERGUNTA PQAL:\nTerapia?\n\nCONTEXTO DO ESTUDO:\nEstudo sobre opióides."
    )
    rota = classificar_roteamento(
        "Terapia de falta de ar?\n\nContexto: Estudo sobre opióides.",
        ctx,
        ["preparar_contexto_pqal"],
    )
    assert rota.usar_ori_pqal is True


def test_roteamento_pqal_sem_contexto():
    ctx = (
        "### Tool: preparar_contexto_pqal\n**Dados:**\n"
        "PQAL_SEM_CONTEXTO: envie Pergunta e Contexto"
    )
    rota = classificar_roteamento("Terapia de falta de ar?", ctx, ["preparar_contexto_pqal"])
    assert rota.usar_ori_pqal is False
