# Assistente Clínico PQAL — Aplicação LangChain

> Documentação completa do projeto: [../README.md](../README.md)

## Início rápido

```powershell
cd langchain
docker compose up -d
pip install -r requirements.txt
copy .env.example .env
ollama pull llama3.1:8b
# ori-pqal-pt: ver ../ori_pqal-model-pt/README.md
python -m streamlit run app.py
```

## Fluxo LangChain (resumo)

```
Pergunta → agent.py (llama3.1:8b + 12 tools) → router.py → chain.py
                                                              ├─ llama3.1:8b  (dados do sistema)
                                                              └─ ori-pqal-pt  (PQAL com contexto)
```

## Arquivos principais

| Arquivo | Papel na chain |
|---------|----------------|
| `agent.py` | Etapa 1 — coleta via AgentExecutor |
| `router.py` | Etapa 2 — escolhe o modelo de resposta |
| `chain.py` | Etapa 3 — LCEL + streaming |
| `app.py` | UI Streamlit com progresso em tempo real |
| `tools/` | 12 tools (leitura + escrita, sem LLM) |

## Testes

```powershell
python -m pytest tests/ -v
```
