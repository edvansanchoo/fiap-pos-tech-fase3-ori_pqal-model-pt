# Assistente Clínico PQAL — MVP

Chat web com LangChain + ori-pqal-pt consultando dados clínicos em PostgreSQL/pgvector.

## Pré-requisitos

- Docker Desktop
- Python 3.11+
- Ollama com modelo `ori-pqal-pt` (ver `../reame-conversao.md`)

## Como executar

```powershell
cd langchain
docker compose up -d
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Abra http://localhost:8501

## Testes

```powershell
pytest tests/ -v
```

## Arquitetura

- `app.py` — interface Streamlit
- `agent.py` — agente ReAct com tools controladas
- `db/queries.py` — único lugar com SQL
- `init.sql` — schema + pgvector + dados de exemplo

O LLM nunca gera SQL livre. A coluna `embedding` em `prontuario` está preparada para busca semântica futura.
