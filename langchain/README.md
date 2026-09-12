# Assistente Clínico PQAL — MVP

Chat web com LangChain chain de dois estágios + PostgreSQL/pgvector.

## Pré-requisitos

- Docker Desktop
- Python 3.11+
- Ollama com:
  - `llama3.1:8b` (agente — decide e executa tools)
  - `ori-pqal-pt` (resposta final)

```powershell
ollama pull llama3.1:8b
# ori-pqal-pt: ver ../reame-conversao.md
```

## Como executar

```powershell
cd langchain
docker compose up -d
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Abra http://localhost:8501

## Arquitetura (Chain LangChain)

```
Pergunta do usuário
        │
        ▼
┌─────────────────────────────┐
│ Etapa 1 — Agente            │
│ llama3.1:8b + tools         │
│ Coleta dados estruturados   │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ Roteamento inteligente      │
│ Dados do sistema?           │
│ PQAL com contexto clínico?  │
└──────┬──────────────┬───────┘
       │              │
  dados sistema    PQAL/saúde
       │              │
       ▼              ▼
 llama3.1:8b    ori-pqal-pt
 (formata)       (sim/não/talvez)
```

- **Dados do banco** (pacientes, exames, medicamentos): resposta via `llama3.1:8b`, sem `ori-pqal-pt`
- **PQAL** (pergunta + contexto científico, estilo dataset de treino): resposta via `ori-pqal-pt`

- `chain.py` — chain LCEL (`clinical_chain`)
- `agent.py` — etapa 1: coleta via tools
- `tools/` — LangChain tools (leitura e escrita no banco, sem LLM no tool)
- `db/queries.py` — SQL parametrizado

## Cadastro e atualização (via chat)

O agente pode gravar no PostgreSQL:

| Ação | Exemplo de pergunta |
|------|---------------------|
| Novo paciente | `Cadastre Ana Costa, nascida em 15/05/1980` |
| Atualizar paciente | `Atualize o paciente 1 para o nome João Silva Santos` |
| Novo exame | `Registre glicemia 110 mg/dL para o paciente 2` |
| Novo medicamento | `Adicione Losartana 50mg ao paciente 1` |

Datas aceitas: `YYYY-MM-DD` ou `DD/MM/YYYY`.

## Testes

```powershell
python -m pytest tests/ -v
```
