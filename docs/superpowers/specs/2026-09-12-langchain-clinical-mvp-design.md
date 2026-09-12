# Design: MVP LangChain + ori-pqal-pt com PostgreSQL/pgvector

**Data:** 2026-09-12  
**Status:** Aprovado  
**Escopo:** MVP de assistente clínico com tools LangChain, interface Streamlit e banco PostgreSQL com pgvector preparado para uso futuro.

---

## Contexto

O projeto `ori-pqal-pt` é um modelo LoRA (Llama 3 8B) fine-tuned para Q&A clínico no formato sim/não/talvez, executado via Ollama. O arquivo `langchain/ideia.md` descreve a arquitetura desejada: consultar dados clínicos estruturados via tools controladas (sem SQL livre gerado pelo LLM) e montar contexto atualizado para o modelo.

### Decisões do usuário

| Decisão | Escolha |
|---------|---------|
| Interface | Streamlit (web mínima) |
| Banco | PostgreSQL 16 + pgvector via Docker Compose |
| Escopo funcional | Consultas pontuais + análise consolidada + liberdade para outras perguntas |
| Modelo | `ori-pqal-pt` (Ollama) |
| Abordagem | Híbrida (agente ReAct + tool dedicada de análise) |

---

## Arquitetura

```
┌──────────────┐      ┌─────────────────────────┐      ┌──────────────┐
│  Streamlit   │─────▶│  LangChain ReAct Agent  │─────▶│ ori-pqal-pt  │
│  (chat web)  │      │  + 5 tools controladas  │      │  (Ollama)    │
└──────────────┘      └───────────┬─────────────┘      └──────────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  PostgreSQL 16        │
                      │  + extensão pgvector  │
                      │  (Docker Compose)     │
                      └───────────────────────┘
```

**Princípio central:** o LLM nunca gera SQL. Toda consulta ao banco passa por funções Python com queries parametrizadas em `db/queries.py`.

---

## Banco de dados

### Infraestrutura

- **Imagem Docker:** `pgvector/pgvector:pg16`
- **Inicialização:** script `init.sql` montado via volume no `docker-compose.yml`
- **Extensão:** `CREATE EXTENSION IF NOT EXISTS vector;`

### Schema

```sql
CREATE TABLE paciente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    data_nascimento DATE NOT NULL
);

CREATE TABLE prontuario (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    data TIMESTAMP NOT NULL,
    descricao TEXT NOT NULL,
    embedding vector(384)  -- NULL no MVP; preparado para busca semântica futura
);

CREATE TABLE exame (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    data DATE NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    resultado TEXT NOT NULL
);

CREATE TABLE medicamento (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    medicamento VARCHAR(255) NOT NULL,
    dose VARCHAR(100) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE  -- NULL = medicamento ativo
);

CREATE TABLE consulta (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    data TIMESTAMP NOT NULL,
    pressao_sistolica INTEGER,
    pressao_diastolica INTEGER,
    observacoes TEXT
);
```

### Seed data

2–3 pacientes fictícios para demonstração, incluindo **João** (68 anos) com dados do exemplo em `ideia.md`:

- Última consulta: 10/09/2026, pressão 145/90
- Medicamento A — 10mg (ativo)
- Último exame: Glicemia = 132 mg/dL
- Entradas de prontuário e exames adicionais para consultas pontuais

A coluna `embedding` permanece `NULL` em todos os registros no MVP.

---

## Tools LangChain

| Tool | Parâmetros | Comportamento |
|------|------------|---------------|
| `buscar_paciente` | `nome_ou_id: str` | Localiza paciente por nome (ILIKE) ou ID numérico |
| `buscar_exames` | `paciente_id: int`, `limite: int = 5` | Retorna últimos exames formatados |
| `buscar_medicamentos` | `paciente_id: int` | Retorna medicamentos ativos (`data_fim IS NULL`) |
| `buscar_prontuario` | `paciente_id: int`, `limite: int = 5` | Retorna entradas recentes do prontuário |
| `analisar_paciente` | `paciente_id: int` | Agrega todos os dados, monta bloco `CONTEXTO ATUAL DO PACIENTE` e invoca `ori-pqal-pt` |

### Tool `analisar_paciente` (detalhe)

Monta contexto estruturado conforme `ideia.md` seção 6:

```
CONTEXTO ATUAL DO PACIENTE

Paciente: João
Idade: 68

Última consulta:
10/09/2026

Pressão:
145/90

Medicamentos:
Medicamento A - 10mg

Último exame:
Glicemia: 132 mg/dL
```

System prompt enviado ao modelo:

```
Você é um assistente de análise de informações clínicas.
Utilize exclusivamente os dados fornecidos no contexto.
Não invente informações.
Não utilize conhecimento externo para preencher informações ausentes.
```

---

## Estrutura de pastas

```
langchain/
├── app.py                  # Streamlit — chat UI
├── agent.py                # Configuração do agente ReAct
├── config.py               # Variáveis de ambiente (DB URL, modelo Ollama)
├── tools/
│   ├── __init__.py
│   ├── paciente.py
│   ├── exames.py
│   ├── medicamentos.py
│   ├── prontuario.py
│   └── analise.py
├── db/
│   ├── connection.py       # Conexão psycopg2
│   └── queries.py          # SQL parametrizado (único lugar com SQL)
├── docker-compose.yml
├── init.sql                # Schema + pgvector + seed
├── requirements.txt
├── .env.example
└── README.md
```

---

## Interface Streamlit

### Layout

- **Área principal:** chat com histórico (`st.chat_message`)
- **Sidebar:**
  - Status de conexão (Postgres + Ollama)
  - Lista de pacientes de exemplo
  - Perguntas sugeridas (clicáveis)

### Perguntas sugeridas

1. "Quais foram os últimos exames do paciente João?"
2. "Quais medicamentos o paciente 1 está tomando?"
3. "Faça uma análise do estado atual do paciente João."

### Verificações na inicialização

- Postgres acessível na URL configurada
- Ollama respondendo e modelo `ori-pqal-pt` disponível

---

## Fluxo de dados

### Consulta pontual

```
Usuário → Streamlit → Agente ReAct → escolhe tool → queries.py (SQL) → Postgres
         → resultado → Agente formata → resposta na UI
```

### Análise consolidada

```
Usuário → Streamlit → Agente ReAct → analisar_paciente(id)
         → agrega dados de todas as tabelas → monta CONTEXTO
         → ori-pqal-pt → resposta na UI
```

### System prompt do agente

- Use tools para obter dados; não invente informações clínicas
- Para análises de estado do paciente, use `analisar_paciente`
- Responda em português brasileiro

---

## Dependências Python (requirements.txt)

```
streamlit
langchain
langchain-ollama
langchain-community
psycopg2-binary
python-dotenv
```

---

## Variáveis de ambiente (.env.example)

```
DATABASE_URL=postgresql://pqal:pqal@localhost:5432/pqal
OLLAMA_MODEL=ori-pqal-pt
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Tratamento de erros

| Situação | Comportamento |
|----------|---------------|
| Postgres offline | Mensagem na UI: "Banco indisponível — execute `docker compose up -d`" |
| Ollama offline | Mensagem: "Ollama indisponível ou modelo ori-pqal-pt não encontrado" |
| Paciente não encontrado | Tool retorna texto claro; agente repassa ao usuário |
| Pergunta fora do escopo clínico | Agente informa que só tem acesso aos dados do banco |

---

## Fora do escopo do MVP

- Autenticação e controle de acesso
- Geração ou consulta de embeddings (pgvector habilitado, mas não utilizado)
- SQL livre gerado pelo LLM
- Deploy em produção
- Integração com sistemas hospitalares reais (HL7/FHIR)

---

## Como executar

```powershell
cd langchain
docker compose up -d
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

**Pré-requisitos:**

1. Docker Desktop em execução
2. Ollama com modelo `ori-pqal-pt` criado (ver `reame-conversao.md`)

---

## Evolução futura (pgvector)

Quando necessário, adicionar:

1. Pipeline de embedding (ex.: `nomic-embed-text` via Ollama) ao inserir prontuários
2. Tool `buscar_prontuario_semantico(query, paciente_id)` com `ORDER BY embedding <=> $query_embedding`
3. Índice HNSW na coluna `prontuario.embedding`

A infraestrutura (extensão + coluna) já estará pronta após o MVP.
