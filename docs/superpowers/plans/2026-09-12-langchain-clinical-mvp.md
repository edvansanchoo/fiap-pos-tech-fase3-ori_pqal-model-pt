# LangChain Clinical MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit chat MVP that uses a LangChain ReAct agent with controlled SQL tools against PostgreSQL/pgvector, powered by the `ori-pqal-pt` Ollama model.

**Architecture:** Streamlit UI calls a LangChain ReAct agent backed by `ChatOllama(model="ori-pqal-pt")`. The agent selects from five predefined tools; all SQL lives in `db/queries.py`. PostgreSQL 16 runs via Docker Compose with the pgvector extension enabled and an unused `embedding` column for future semantic search.

**Tech Stack:** Python 3.11+, Streamlit, LangChain, langchain-ollama, psycopg2-binary, PostgreSQL 16, pgvector, Docker Compose, pytest

## Global Constraints

- Model name: `ori-pqal-pt` via Ollama (`OLLAMA_BASE_URL=http://localhost:11434`)
- Database URL: `postgresql://pqal:pqal@localhost:5432/pqal`
- Docker image: `pgvector/pgvector:pg16`
- LLM must never generate free-form SQL; all queries are parameterized in `db/queries.py`
- `embedding vector(384)` column exists but stays `NULL` in MVP
- UI language: Brazilian Portuguese
- Respond in Portuguese in agent outputs

## File Map

| File | Responsibility |
|------|----------------|
| `langchain/docker-compose.yml` | Postgres + pgvector container |
| `langchain/init.sql` | Schema, extension, seed data |
| `langchain/config.py` | Load env vars |
| `langchain/db/connection.py` | psycopg2 connection helper |
| `langchain/db/queries.py` | All parameterized SQL |
| `langchain/tools/paciente.py` | `buscar_paciente` tool |
| `langchain/tools/exames.py` | `buscar_exames` tool |
| `langchain/tools/medicamentos.py` | `buscar_medicamentos` tool |
| `langchain/tools/prontuario.py` | `buscar_prontuario` tool |
| `langchain/tools/analise.py` | `analisar_paciente` tool |
| `langchain/tools/__init__.py` | Export all tools |
| `langchain/agent.py` | ReAct agent factory |
| `langchain/app.py` | Streamlit chat UI |
| `langchain/requirements.txt` | Python dependencies |
| `langchain/.env.example` | Env template |
| `langchain/README.md` | Run instructions |
| `langchain/tests/test_queries.py` | Query unit/integration tests |
| `langchain/tests/conftest.py` | pytest fixtures |

---

### Task 1: Project Scaffold and Config

**Files:**
- Create: `langchain/requirements.txt`
- Create: `langchain/.env.example`
- Create: `langchain/config.py`
- Create: `langchain/db/__init__.py` (empty)
- Create: `langchain/tools/__init__.py` (empty)
- Create: `langchain/tests/conftest.py`

**Interfaces:**
- Consumes: nothing
- Produces: `config.DATABASE_URL: str`, `config.OLLAMA_MODEL: str`, `config.OLLAMA_BASE_URL: str`

- [ ] **Step 1: Create `langchain/requirements.txt`**

```
streamlit>=1.32.0
langchain>=0.3.0
langchain-ollama>=0.2.0
langchain-community>=0.3.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Create `langchain/.env.example`**

```
DATABASE_URL=postgresql://pqal:pqal@localhost:5432/pqal
OLLAMA_MODEL=ori-pqal-pt
OLLAMA_BASE_URL=http://localhost:11434
```

- [ ] **Step 3: Create `langchain/config.py`**

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pqal:pqal@localhost:5432/pqal")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ori-pqal-pt")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
```

- [ ] **Step 4: Create empty package markers**

Create empty files:
- `langchain/db/__init__.py`
- `langchain/tools/__init__.py`

- [ ] **Step 5: Create `langchain/tests/conftest.py`**

```python
import os
import pytest

@pytest.fixture(scope="session")
def database_url():
    return os.getenv("DATABASE_URL", "postgresql://pqal:pqal@localhost:5432/pqal")
```

- [ ] **Step 6: Install dependencies**

Run from `langchain/`:

```powershell
pip install -r requirements.txt
copy .env.example .env
```

Expected: packages install without error.

- [ ] **Step 7: Commit**

```powershell
git add langchain/requirements.txt langchain/.env.example langchain/config.py langchain/db/__init__.py langchain/tools/__init__.py langchain/tests/conftest.py
git commit -m "chore: scaffold langchain MVP project"
```

---

### Task 2: Docker Compose and Database Seed

**Files:**
- Create: `langchain/docker-compose.yml`
- Create: `langchain/init.sql`

**Interfaces:**
- Consumes: nothing
- Produces: running Postgres on port 5432 with tables `paciente`, `prontuario`, `exame`, `medicamento`, `consulta` and seed patient "João" (id=1)

- [ ] **Step 1: Create `langchain/docker-compose.yml`**

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    container_name: pqal-postgres
    environment:
      POSTGRES_USER: pqal
      POSTGRES_PASSWORD: pqal
      POSTGRES_DB: pqal
    ports:
      - "5432:5432"
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pqal -d pqal"]
      interval: 5s
      timeout: 5s
      retries: 5
```

- [ ] **Step 2: Create `langchain/init.sql`**

```sql
CREATE EXTENSION IF NOT EXISTS vector;

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
    embedding vector(384)
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
    data_fim DATE
);

CREATE TABLE consulta (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    data TIMESTAMP NOT NULL,
    pressao_sistolica INTEGER,
    pressao_diastolica INTEGER,
    observacoes TEXT
);

-- Paciente 1: João (68 anos em 2026)
INSERT INTO paciente (nome, data_nascimento) VALUES
    ('João Silva', '1958-03-15'),
    ('Maria Santos', '1972-07-22'),
    ('Pedro Oliveira', '1990-11-08');

INSERT INTO consulta (paciente_id, data, pressao_sistolica, pressao_diastolica, observacoes) VALUES
    (1, '2026-09-10 14:30:00', 145, 90, 'Paciente relata fadiga leve.'),
    (2, '2026-09-05 10:00:00', 120, 80, 'Consulta de rotina.'),
    (3, '2026-08-28 09:15:00', 118, 76, 'Sem queixas.');

INSERT INTO medicamento (paciente_id, medicamento, dose, data_inicio, data_fim) VALUES
    (1, 'Medicamento A', '10mg', '2026-06-01', NULL),
    (1, 'Losartana', '50mg', '2025-01-10', '2026-05-31'),
    (2, 'Metformina', '850mg', '2026-03-01', NULL);

INSERT INTO exame (paciente_id, data, tipo, resultado) VALUES
    (1, '2026-09-08', 'Glicemia', '132 mg/dL'),
    (1, '2026-08-20', 'Glicemia', '95 mg/dL'),
    (1, '2026-09-01', 'Hemograma', 'Hemoglobina: 13.8 g/dL'),
    (2, '2026-09-02', 'Hemoglobina glicada', '6.2%'),
    (3, '2026-08-15', 'Colesterol total', '190 mg/dL');

INSERT INTO prontuario (paciente_id, data, descricao) VALUES
    (1, '2026-09-10 14:45:00', 'Paciente com hipertensão controlada parcialmente. Orientado sobre dieta.'),
    (1, '2026-08-20 11:00:00', 'Retorno ambulatorial. Glicemia dentro da normalidade.'),
    (2, '2026-09-05 10:30:00', 'Diabetes tipo 2 em acompanhamento. Adesão ao tratamento adequada.');
```

- [ ] **Step 3: Start database and verify**

Run from `langchain/`:

```powershell
docker compose up -d
docker compose ps
```

Expected: container `pqal-postgres` healthy.

Verify seed:

```powershell
docker exec pqal-postgres psql -U pqal -d pqal -c "SELECT id, nome FROM paciente;"
```

Expected output includes `João Silva` with id `1`.

Verify pgvector:

```powershell
docker exec pqal-postgres psql -U pqal -d pqal -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

Expected: one row `vector`.

- [ ] **Step 4: Commit**

```powershell
git add langchain/docker-compose.yml langchain/init.sql
git commit -m "feat: add PostgreSQL pgvector docker setup with seed data"
```

---

### Task 3: Database Connection Layer

**Files:**
- Create: `langchain/db/connection.py`
- Create: `langchain/tests/test_connection.py`

**Interfaces:**
- Consumes: `config.DATABASE_URL`
- Produces: `get_connection() -> psycopg2.extensions.connection`, `check_db_connection() -> bool`

- [ ] **Step 1: Write failing test `langchain/tests/test_connection.py`**

```python
from db.connection import check_db_connection

def test_check_db_connection():
    assert check_db_connection() is True
```

- [ ] **Step 2: Run test to verify it fails**

```powershell
cd langchain
pytest tests/test_connection.py::test_check_db_connection -v
```

Expected: FAIL with `ImportError` or `check_db_connection` not defined.

- [ ] **Step 3: Create `langchain/db/connection.py`**

```python
import psycopg2
from config import DATABASE_URL


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def check_db_connection() -> bool:
    try:
        conn = get_connection()
        conn.close()
        return True
    except psycopg2.Error:
        return False
```

- [ ] **Step 4: Run test to verify it passes**

```powershell
pytest tests/test_connection.py::test_check_db_connection -v
```

Expected: PASS (requires Docker Postgres running).

- [ ] **Step 5: Commit**

```powershell
git add langchain/db/connection.py langchain/tests/test_connection.py
git commit -m "feat: add database connection helper"
```

---

### Task 4: Parameterized Queries

**Files:**
- Create: `langchain/db/queries.py`
- Create: `langchain/tests/test_queries.py`

**Interfaces:**
- Consumes: `db.connection.get_connection()`
- Produces:
  - `buscar_paciente_por_id(paciente_id: int) -> dict | None`
  - `buscar_paciente_por_nome(nome: str) -> list[dict]`
  - `listar_pacientes() -> list[dict]`
  - `buscar_exames(paciente_id: int, limite: int = 5) -> list[dict]`
  - `buscar_medicamentos_ativos(paciente_id: int) -> list[dict]`
  - `buscar_prontuario(paciente_id: int, limite: int = 5) -> list[dict]`
  - `buscar_ultima_consulta(paciente_id: int) -> dict | None`
  - `calcular_idade(data_nascimento) -> int` (helper using `date.today()`)

- [ ] **Step 1: Write failing tests `langchain/tests/test_queries.py`**

```python
from datetime import date
from db import queries


def test_buscar_paciente_por_id_encontra_joao():
    paciente = queries.buscar_paciente_por_id(1)
    assert paciente is not None
    assert paciente["nome"] == "João Silva"


def test_buscar_paciente_por_nome_encontra_joao():
    resultados = queries.buscar_paciente_por_nome("joão")
    assert len(resultados) >= 1
    assert resultados[0]["nome"] == "João Silva"


def test_buscar_exames_retorna_glicemia():
    exames = queries.buscar_exames(1, limite=3)
    assert len(exames) >= 1
    assert any("Glicemia" in e["tipo"] for e in exames)


def test_buscar_medicamentos_ativos_retorna_medicamento_a():
    meds = queries.buscar_medicamentos_ativos(1)
    assert any(m["medicamento"] == "Medicamento A" for m in meds)
    assert all(m["data_fim"] is None for m in meds)


def test_buscar_ultima_consulta_joao():
    consulta = queries.buscar_ultima_consulta(1)
    assert consulta is not None
    assert consulta["pressao_sistolica"] == 145
    assert consulta["pressao_diastolica"] == 90


def test_calcular_idade():
    idade = queries.calcular_idade(date(1958, 3, 15))
    assert idade == 68
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/test_queries.py -v
```

Expected: FAIL — module/functions missing.

- [ ] **Step 3: Create `langchain/db/queries.py`**

```python
from datetime import date
from db.connection import get_connection


def _row_to_dict(cursor, row):
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def calcular_idade(data_nascimento: date) -> int:
    hoje = date.today()
    idade = hoje.year - data_nascimento.year
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return idade


def buscar_paciente_por_id(paciente_id: int) -> dict | None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, data_nascimento FROM paciente WHERE id = %s",
                (paciente_id,),
            )
            row = cur.fetchone()
            return _row_to_dict(cur, row) if row else None
    finally:
        conn.close()


def buscar_paciente_por_nome(nome: str) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, data_nascimento FROM paciente WHERE nome ILIKE %s ORDER BY id",
                (f"%{nome}%",),
            )
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def listar_pacientes() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, data_nascimento FROM paciente ORDER BY id")
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def buscar_exames(paciente_id: int, limite: int = 5) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, paciente_id, data, tipo, resultado
                FROM exame
                WHERE paciente_id = %s
                ORDER BY data DESC
                LIMIT %s
                """,
                (paciente_id, limite),
            )
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def buscar_medicamentos_ativos(paciente_id: int) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, paciente_id, medicamento, dose, data_inicio, data_fim
                FROM medicamento
                WHERE paciente_id = %s AND data_fim IS NULL
                ORDER BY data_inicio DESC
                """,
                (paciente_id,),
            )
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def buscar_prontuario(paciente_id: int, limite: int = 5) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, paciente_id, data, descricao
                FROM prontuario
                WHERE paciente_id = %s
                ORDER BY data DESC
                LIMIT %s
                """,
                (paciente_id, limite),
            )
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def buscar_ultima_consulta(paciente_id: int) -> dict | None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, paciente_id, data, pressao_sistolica, pressao_diastolica, observacoes
                FROM consulta
                WHERE paciente_id = %s
                ORDER BY data DESC
                LIMIT 1
                """,
                (paciente_id,),
            )
            row = cur.fetchone()
            return _row_to_dict(cur, row) if row else None
    finally:
        conn.close()
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/test_queries.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add langchain/db/queries.py langchain/tests/test_queries.py
git commit -m "feat: add parameterized clinical queries"
```

---

### Task 5: LangChain Tools

**Files:**
- Create: `langchain/tools/paciente.py`
- Create: `langchain/tools/exames.py`
- Create: `langchain/tools/medicamentos.py`
- Create: `langchain/tools/prontuario.py`
- Create: `langchain/tools/analise.py`
- Modify: `langchain/tools/__init__.py`
- Create: `langchain/tests/test_tools.py`

**Interfaces:**
- Consumes: all functions from `db.queries`, `config.OLLAMA_MODEL`, `config.OLLAMA_BASE_URL`
- Produces: five `@tool` decorated functions exported from `tools/__init__.py`

- [ ] **Step 1: Create `langchain/tools/paciente.py`**

```python
from langchain_core.tools import tool
from db import queries


@tool
def buscar_paciente(nome_ou_id: str) -> str:
    """Busca paciente por nome (parcial) ou ID numérico. Retorna dados básicos do paciente."""
    nome_ou_id = nome_ou_id.strip()
    if nome_ou_id.isdigit():
        paciente = queries.buscar_paciente_por_id(int(nome_ou_id))
        if not paciente:
            return f"Paciente com ID {nome_ou_id} não encontrado."
        idade = queries.calcular_idade(paciente["data_nascimento"])
        return f"ID: {paciente['id']}\nNome: {paciente['nome']}\nIdade: {idade} anos"

    resultados = queries.buscar_paciente_por_nome(nome_ou_id)
    if not resultados:
        return f"Nenhum paciente encontrado com nome contendo '{nome_ou_id}'."

    linhas = []
    for p in resultados:
        idade = queries.calcular_idade(p["data_nascimento"])
        linhas.append(f"ID: {p['id']} | Nome: {p['nome']} | Idade: {idade} anos")
    return "\n".join(linhas)
```

- [ ] **Step 2: Create `langchain/tools/exames.py`**

```python
from langchain_core.tools import tool
from db import queries


@tool
def buscar_exames(paciente_id: int, limite: int = 5) -> str:
    """Busca os exames mais recentes de um paciente pelo ID."""
    exames = queries.buscar_exames(paciente_id, limite=limite)
    if not exames:
        return f"Nenhum exame encontrado para o paciente {paciente_id}."

    linhas = []
    for e in exames:
        linhas.append(f"{e['data']} - {e['tipo']}:\n{e['resultado']}")
    return "\n\n".join(linhas)
```

- [ ] **Step 3: Create `langchain/tools/medicamentos.py`**

```python
from langchain_core.tools import tool
from db import queries


@tool
def buscar_medicamentos(paciente_id: int) -> str:
    """Busca medicamentos ativos de um paciente pelo ID."""
    meds = queries.buscar_medicamentos_ativos(paciente_id)
    if not meds:
        return f"Nenhum medicamento ativo encontrado para o paciente {paciente_id}."

    linhas = []
    for m in meds:
        linhas.append(f"{m['medicamento']} - {m['dose']} (desde {m['data_inicio']})")
    return "\n".join(linhas)
```

- [ ] **Step 4: Create `langchain/tools/prontuario.py`**

```python
from langchain_core.tools import tool
from db import queries


@tool
def buscar_prontuario(paciente_id: int, limite: int = 5) -> str:
    """Busca entradas recentes do prontuário de um paciente pelo ID."""
    entradas = queries.buscar_prontuario(paciente_id, limite=limite)
    if not entradas:
        return f"Nenhuma entrada de prontuário encontrada para o paciente {paciente_id}."

    linhas = []
    for e in entradas:
        linhas.append(f"{e['data']}:\n{e['descricao']}")
    return "\n\n".join(linhas)
```

- [ ] **Step 5: Create `langchain/tools/analise.py`**

```python
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from db import queries

SYSTEM_PROMPT = """Você é um assistente de análise de informações clínicas.
Utilize exclusivamente os dados fornecidos no contexto.
Não invente informações.
Não utilize conhecimento externo para preencher informações ausentes."""


def _montar_contexto(paciente_id: int) -> str:
    paciente = queries.buscar_paciente_por_id(paciente_id)
    if not paciente:
        return ""

    idade = queries.calcular_idade(paciente["data_nascimento"])
    consulta = queries.buscar_ultima_consulta(paciente_id)
    meds = queries.buscar_medicamentos_ativos(paciente_id)
    exames = queries.buscar_exames(paciente_id, limite=1)

    linhas = [
        "CONTEXTO ATUAL DO PACIENTE",
        "",
        f"Paciente: {paciente['nome']}",
        f"Idade: {idade}",
    ]

    if consulta:
        data_fmt = consulta["data"].strftime("%d/%m/%Y")
        linhas.extend(["", "Última consulta:", data_fmt])
        if consulta["pressao_sistolica"] and consulta["pressao_diastolica"]:
            linhas.extend([
                "",
                "Pressão:",
                f"{consulta['pressao_sistolica']}/{consulta['pressao_diastolica']}",
            ])

    if meds:
        linhas.extend(["", "Medicamentos:"])
        for m in meds:
            linhas.append(f"{m['medicamento']} - {m['dose']}")

    if exames:
        ultimo = exames[0]
        linhas.extend([
            "",
            "Último exame:",
            f"{ultimo['tipo']}: {ultimo['resultado']}",
        ])

    return "\n".join(linhas)


@tool
def analisar_paciente(paciente_id: int) -> str:
    """Agrega todos os dados clínicos do paciente e gera uma análise do estado atual."""
    contexto = _montar_contexto(paciente_id)
    if not contexto:
        return f"Paciente {paciente_id} não encontrado."

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    prompt = f"""{SYSTEM_PROMPT}

CONTEXTO:
{contexto}

PERGUNTA:
Faça uma análise do estado atual do paciente."""

    response = llm.invoke(prompt)
    return response.content
```

- [ ] **Step 6: Update `langchain/tools/__init__.py`**

```python
from tools.paciente import buscar_paciente
from tools.exames import buscar_exames
from tools.medicamentos import buscar_medicamentos
from tools.prontuario import buscar_prontuario
from tools.analise import analisar_paciente

ALL_TOOLS = [
    buscar_paciente,
    buscar_exames,
    buscar_medicamentos,
    buscar_prontuario,
    analisar_paciente,
]
```

- [ ] **Step 7: Write test `langchain/tests/test_tools.py`**

```python
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
```

- [ ] **Step 8: Run tool tests**

```powershell
pytest tests/test_tools.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 9: Commit**

```powershell
git add langchain/tools/ langchain/tests/test_tools.py
git commit -m "feat: add LangChain clinical tools"
```

---

### Task 6: ReAct Agent

**Files:**
- Create: `langchain/agent.py`
- Create: `langchain/health.py`

**Interfaces:**
- Consumes: `tools.ALL_TOOLS`, `config.OLLAMA_MODEL`, `config.OLLAMA_BASE_URL`
- Produces: `create_agent_executor() -> AgentExecutor`, `check_ollama_available() -> bool`

- [ ] **Step 1: Create `langchain/health.py`**

```python
import urllib.request
import json
from config import OLLAMA_BASE_URL, OLLAMA_MODEL


def check_ollama_available() -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=3) as resp:
            data = json.loads(resp.read().decode())
            models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
            return OLLAMA_MODEL in models or f"{OLLAMA_MODEL}:latest" in [
                m.get("name", "") for m in data.get("models", [])
            ]
    except Exception:
        return False
```

- [ ] **Step 2: Create `langchain/agent.py`**

```python
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from tools import ALL_TOOLS

AGENT_PROMPT = PromptTemplate.from_template("""Você é um assistente clínico que responde perguntas sobre pacientes.
Use as ferramentas disponíveis para buscar dados no banco. Não invente informações clínicas.
Para análises do estado atual do paciente, use a ferramenta analisar_paciente.
Responda sempre em português brasileiro.

Ferramentas disponíveis:
{tools}

Nomes das ferramentas: {tool_names}

Formato de raciocínio:
Pergunta: a pergunta do usuário
Thought: pense no que precisa fazer
Action: nome da ferramenta
Action Input: entrada da ferramenta
Observation: resultado da ferramenta
... (repita Thought/Action/Action Input/Observation conforme necessário)
Thought: agora sei a resposta final
Final Answer: resposta final ao usuário

Pergunta: {input}
Thought: {agent_scratchpad}""")


def create_agent_executor() -> AgentExecutor:
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )
    agent = create_react_agent(llm, ALL_TOOLS, AGENT_PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=6,
    )
```

- [ ] **Step 3: Smoke test agent manually**

Run from `langchain/` (requires Ollama with `ori-pqal-pt`):

```powershell
python -c "from agent import create_agent_executor; e = create_agent_executor(); print(e.invoke({'input': 'Quais medicamentos o paciente 1 esta tomando?'})['output'])"
```

Expected: response mentioning Medicamento A.

- [ ] **Step 4: Commit**

```powershell
git add langchain/agent.py langchain/health.py
git commit -m "feat: add ReAct agent with ori-pqal-pt"
```

---

### Task 7: Streamlit Chat UI

**Files:**
- Create: `langchain/app.py`

**Interfaces:**
- Consumes: `agent.create_agent_executor()`, `db.connection.check_db_connection()`, `health.check_ollama_available()`, `db.queries.listar_pacientes()`

- [ ] **Step 1: Create `langchain/app.py`**

```python
import streamlit as st
from agent import create_agent_executor
from db.connection import check_db_connection
from db import queries
from health import check_ollama_available

st.set_page_config(page_title="Assistente Clínico PQAL", page_icon="🏥", layout="wide")
st.title("Assistente Clínico PQAL")
st.caption("LangChain + ori-pqal-pt + PostgreSQL/pgvector")

SUGESTOES = [
    "Quais foram os últimos exames do paciente João?",
    "Quais medicamentos o paciente 1 está tomando?",
    "Faça uma análise do estado atual do paciente João.",
]

with st.sidebar:
    st.header("Status")
    db_ok = check_db_connection()
    ollama_ok = check_ollama_available()
    st.write("🟢 Banco de dados" if db_ok else "🔴 Banco indisponível — execute `docker compose up -d`")
    st.write("🟢 Ollama / ori-pqal-pt" if ollama_ok else "🔴 Ollama indisponível ou modelo ori-pqal-pt não encontrado")

    st.header("Pacientes de exemplo")
    if db_ok:
        for p in queries.listar_pacientes():
            idade = queries.calcular_idade(p["data_nascimento"])
            st.write(f"**{p['id']}** — {p['nome']} ({idade} anos)")

    st.header("Perguntas sugeridas")
    for sugestao in SUGESTOES:
        if st.button(sugestao, key=sugestao):
            st.session_state["sugestao"] = sugestao

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Faça uma pergunta sobre os pacientes...")
if "sugestao" in st.session_state:
    prompt = st.session_state.pop("sugestao")

if prompt:
    if not db_ok:
        st.error("Banco indisponível — execute `docker compose up -d` na pasta langchain.")
        st.stop()
    if not ollama_ok:
        st.error("Ollama indisponível ou modelo ori-pqal-pt não encontrado.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando dados..."):
            executor = create_agent_executor()
            result = executor.invoke({"input": prompt})
            resposta = result["output"]
        st.markdown(resposta)

    st.session_state.messages.append({"role": "assistant", "content": resposta})
```

- [ ] **Step 2: Run Streamlit**

```powershell
cd langchain
streamlit run app.py
```

Manual checks in browser at `http://localhost:8501`:
1. Sidebar shows green status for DB and Ollama
2. Patient list shows João, Maria, Pedro
3. Clicking suggested question "Quais medicamentos o paciente 1 está tomando?" returns Medicamento A
4. "Faça uma análise do estado atual do paciente João." returns analysis based on context

- [ ] **Step 3: Commit**

```powershell
git add langchain/app.py
git commit -m "feat: add Streamlit chat UI"
```

---

### Task 8: README and Final Verification

**Files:**
- Create: `langchain/README.md`

- [ ] **Step 1: Create `langchain/README.md`**

```markdown
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
```

- [ ] **Step 2: Run full test suite**

```powershell
cd langchain
pytest tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 3: Commit**

```powershell
git add langchain/README.md
git commit -m "docs: add langchain MVP README"
```

---

## Self-Review

**Spec coverage:**
- Streamlit UI → Task 7
- Docker + pgvector → Task 2
- 5 tools → Task 5
- ReAct agent → Task 6
- Seed João data → Task 2 init.sql
- Error messages in UI → Task 7 app.py
- No free SQL from LLM → Task 4 queries.py only
- pgvector column unused → init.sql embedding NULL

**Placeholder scan:** No TBD/TODO found.

**Type consistency:** Tool signatures match spec; query functions used consistently across tools and tests.
