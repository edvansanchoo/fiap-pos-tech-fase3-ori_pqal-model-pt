# Assistente Clínico PQAL

MVP de assistente clínico em português que combina **LangChain**, **PostgreSQL/pgvector**, **Streamlit** e **Ollama** com dois modelos especializados:

| Modelo | Variável | Função |
|--------|----------|--------|
| `llama3.1:8b` | `OLLAMA_AGENT_MODEL` | Agente: decide e executa tools, formata respostas de dados do sistema |
| `ori-pqal-pt` | `OLLAMA_MODEL` | Respostas PQAL (sim/não/talvez) com base em contexto científico |

---

## Estrutura do repositório

```
ori_pqal-model-pt-20260912T125149Z-1-001/
├── README.md                 ← este documento
├── reame-conversao.md        ← redireciona para ori_pqal-model-pt/README.md
├── .gitignore                ← exclui modelo, .env, datasets .jsonl
│
├── langchain/                ← aplicação principal (chat + chain)
│   ├── app.py                ← interface Streamlit
│   ├── chain.py              ← chain LCEL (orquestração final)
│   ├── agent.py              ← agente LangChain + coleta de dados
│   ├── router.py             ← roteamento inteligente entre modelos
│   ├── orchestrator.py       ← ponto de entrada programático
│   ├── resposta_sistema.py   ← formatação de respostas (dados do banco)
│   ├── llm_stream.py         ← streaming do ori-pqal-pt
│   ├── ui_progress.py        ← progresso em tempo real na UI
│   ├── agent_callbacks.py    ← callbacks LangChain para tools
│   ├── config.py             ← variáveis de ambiente
│   ├── health.py             ← checagem Ollama + modelos
│   ├── messages.py             ← textos de ajuda e listagens
│   ├── main.py               ← health check CLI
│   │
│   ├── db/
│   │   ├── connection.py     ← conexão PostgreSQL
│   │   └── queries.py        ← SQL parametrizado (leitura + escrita)
│   │
│   ├── tools/                ← LangChain tools (sem LLM dentro)
│   │   ├── __init__.py       ← lista ALL_TOOLS (12 tools)
│   │   ├── schemas.py        ← schemas Pydantic flexíveis
│   │   ├── parse_input.py    ← parsing de ID, data, limite
│   │   ├── sistema.py        ← listar pacientes, ajuda
│   │   ├── paciente.py       ← buscar paciente
│   │   ├── escrita.py        ← criar/atualizar paciente, exame, medicamento
│   │   ├── exames.py         ← buscar exames
│   │   ├── medicamentos.py   ← buscar medicamentos
│   │   ├── prontuario.py     ← buscar prontuário
│   │   ├── analise.py        ← montar contexto clínico completo
│   │   └── pqal.py           ← preparar contexto PQAL
│   │
│   ├── tests/                ← testes pytest
│   ├── docker-compose.yml    ← PostgreSQL 16 + pgvector
│   ├── init.sql              ← schema + dados de exemplo
│   ├── requirements.txt
│   ├── .env.example
│   └── ideia.md              ← especificação original do MVP
│
├── docs/superpowers/         ← documentação de design e plano
│   ├── specs/                ← especificação arquitetural
│   └── plans/                ← plano de implementação
│
├── ori-pqal-model-pt.zip     ← pacote completo do modelo (~151 MB, Git LFS)
└── ori_pqal-model-pt/        ← configs + README (pesos vêm do zip)
    ├── README.md             ← conversão para Ollama + instruções de download
    ├── Modelfile
    ├── adapter_config.json
    └── tokenizer_config.json
```

---

## Fluxo LangChain (visão completa)

### Diagrama de sequência

```mermaid
sequenceDiagram
    participant U as Usuário
    participant ST as Streamlit (app.py)
    participant UI as ui_progress.py
    participant AG as agent.py
    participant T as Tools (12)
    participant DB as PostgreSQL
    participant RT as router.py
    participant CH as chain.py
    participant L1 as llama3.1:8b
    participant L2 as ori-pqal-pt

    U->>ST: Pergunta no chat
    ST->>UI: gather_com_progresso_tempo_real()
    UI->>AG: gather_structured_context()

    alt PQAL com Contexto na mensagem
        AG->>AG: _coletar_pqal_direto() (sem agente)
    else Demais perguntas
        AG->>L1: AgentExecutor (tool calling)
        loop Cada tool necessária
            L1->>T: invoca tool
            T->>DB: SQL parametrizado
            DB-->>T: dados
            T-->>AG: observation
            AG-->>UI: callback progresso (tempo real)
        end
    end

    AG-->>UI: GatherResult (contexto + tools_usadas)
    UI-->>ST: Etapa 1 concluída

    ST->>RT: classificar_roteamento()
    RT-->>ST: usar_ori_pqal? + motivo
    ST-->>U: Etapa 2 exibida na UI

    ST->>CH: stream_resposta_chain()

    alt Dados do sistema / PQAL sem contexto
        CH->>L1: resposta_sistema.py
        L1-->>U: stream resposta formatada
    else PQAL com contexto científico
        CH->>L2: ORI_PROMPT + contexto
        L2-->>U: stream sim/não/talvez
    end
```

### Pipeline em 3 etapas

```
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 1 — COLETA (agent.py)                                    │
│  Modelo: OLLAMA_AGENT_MODEL = llama3.1:8b                       │
│                                                                 │
│  • Interpreta a pergunta                                        │
│  • Executa LangChain tools (AgentExecutor + tool calling)       │
│  • Retorna dados estruturados (intermediate_steps)              │
│  • Atalho: PQAL com "Contexto:" → parse direto (sem agente)     │
└────────────────────────────┬────────────────────────────────────┘
                             │ GatherResult
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 2 — ROTEAMENTO (router.py)                               │
│                                                                 │
│  Decide qual modelo gera a resposta final:                      │
│  ┌─────────────────────────┬────────────────────────────────┐ │
│  │ llama3.1:8b (sistema)   │ ori-pqal-pt (PQAL)             │ │
│  │ • pacientes, exames     │ • Pergunta + Contexto científico│ │
│  │ • medicamentos, ajuda   │ • resposta sim/não/talvez      │ │
│  │ • cadastro/atualização  │ • estilo dataset PQAL          │ │
│  │ • PQAL sem contexto     │                                │ │
│  └─────────────────────────┴────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ entrada dict
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ETAPA 3 — RESPOSTA (chain.py)                                  │
│                                                                 │
│  Se usar_ori_pqal:                                              │
│    ORI_PROMPT | ChatOllama(ori-pqal-pt) | StrOutputParser       │
│                                                                 │
│  Senão:                                                         │
│    resposta_sistema.py → llama3.1:8b formata os dados           │
│    (ou resposta direta se tool retornou texto único)            │
└─────────────────────────────────────────────────────────────────┘
```

### Chain LCEL (`chain.py`)

A chain LangChain Expression Language é definida como:

```python
clinical_chain = RunnableLambda(run_clinical_chain)
```

Internamente:

| Função | Descrição |
|--------|-----------|
| `preparar_entrada_chain()` | Etapas 1+2: coleta + roteamento |
| `stream_resposta_chain()` | Etapa 3: streaming da resposta |
| `run_clinical_chain()` | Execução síncrona completa |
| `run_clinical_chain_stream()` | Generator para streaming |

**Importante:** as tools **não chamam LLM**. Todo uso de modelo acontece em `agent.py` (coleta), `router.py` (fallback LLM) e `chain.py` / `resposta_sistema.py` (resposta).

---

## Pasta `langchain/` — detalhamento por arquivo

### Camada de interface

| Arquivo | Responsabilidade |
|---------|------------------|
| `app.py` | Chat Streamlit; exibe etapas 1–3 em `st.status`; progresso de tools em tempo real; histórico de mensagens |
| `ui_progress.py` | Thread + fila para atualizar UI durante execução bloqueante do agente |
| `main.py` | CLI simples: verifica banco e modelos Ollama |

### Camada LangChain (núcleo)

| Arquivo | Responsabilidade |
|---------|------------------|
| `agent.py` | `AgentExecutor` com `llama3.1:8b`; 12 tools; `gather_structured_context()` retorna `GatherResult`; atalho PQAL; deduplicação de passos |
| `chain.py` | Prompt `ORI_PROMPT` para ori-pqal-pt; orquestra etapa 3; exporta `clinical_chain` |
| `router.py` | Regras determinísticas + fallback LLM; classifica `ori_pqal` vs `sistema` |
| `orchestrator.py` | `run_query()` / `run_query_stream()` — API unificada para testes e integrações |
| `resposta_sistema.py` | Prompt de formatação para dados do banco; resposta direta quando há um único bloco |
| `llm_stream.py` | `stream_prompt()` — streaming token a token do ori-pqal-pt |
| `agent_callbacks.py` | `ToolProgressHandler` — eventos `on_tool_start` / `on_tool_end` |

### Configuração e saúde

| Arquivo | Responsabilidade |
|---------|------------------|
| `config.py` | `DATABASE_URL`, `OLLAMA_MODEL`, `OLLAMA_AGENT_MODEL`, `OLLAMA_BASE_URL` |
| `health.py` | Verifica se Ollama responde e se os dois modelos estão instalados |
| `messages.py` | Texto de ajuda e formatação da lista de pacientes |
| `.env.example` | Template de variáveis (copiar para `.env`) |

### Banco de dados (`db/`)

| Arquivo | Responsabilidade |
|---------|------------------|
| `connection.py` | `get_connection()`, `check_db_connection()` via psycopg2 |
| `queries.py` | Todas as queries SQL parametrizadas |

**Tabelas** (`init.sql`):

| Tabela | Conteúdo |
|--------|----------|
| `paciente` | id, nome, data_nascimento |
| `consulta` | pressão, observações, data |
| `exame` | tipo, resultado, data |
| `medicamento` | nome, dose, data_inicio, data_fim |
| `prontuario` | descrição, data, embedding vector(384) |

**Dados de exemplo:** João Silva (id=1), Maria Santos (id=2), Pedro Oliveira (id=3).

**Operações de escrita** (via `queries.py` + `tools/escrita.py`):

- `criar_paciente`, `atualizar_paciente`
- `registrar_exame`, `registrar_medicamento`

### Tools (`tools/`) — catálogo completo

Todas são `@tool` do LangChain com `args_schema` Pydantic flexível (aceita aliases como `id`, `id_paciente`, `nome_ou_id`).

| Tool | Tipo | Descrição |
|------|------|-----------|
| `listar_pacientes_disponiveis` | leitura | Lista todos os pacientes |
| `mostrar_ajuda` | leitura | Explica capacidades do assistente |
| `buscar_paciente` | leitura | Busca por nome parcial ou ID |
| `criar_paciente` | escrita | Cadastra nome + data de nascimento |
| `atualizar_paciente` | escrita | Altera nome ou data de nascimento |
| `buscar_exames` | leitura | Exames recentes de um paciente |
| `registrar_exame` | escrita | Adiciona exame (tipo, resultado, data) |
| `buscar_medicamentos` | leitura | Medicamentos ativos |
| `registrar_medicamento` | escrita | Adiciona medicamento ativo |
| `buscar_prontuario` | leitura | Entradas recentes do prontuário |
| `montar_contexto_paciente` | leitura | Agrega paciente + consulta + exames + meds + prontuário |
| `preparar_contexto_pqal` | leitura | Extrai Pergunta + Contexto para formato PQAL |

**Arquivos de suporte:**

| Arquivo | Função |
|---------|--------|
| `schemas.py` | Modelos Pydantic com normalização de parâmetros |
| `parse_input.py` | `parse_int_id()`, `parse_data()`, `parse_limite()` |

### Testes (`tests/`)

| Arquivo | Cobertura |
|---------|-----------|
| `test_connection.py` | Conexão PostgreSQL |
| `test_queries.py` | Queries de leitura |
| `test_tools.py` | Tools de leitura + aliases |
| `test_escrita.py` | Tools de escrita |
| `test_parse_input.py` | Parsing de ID e datas |
| `test_agent.py` | Criação do AgentExecutor (12 tools) |
| `test_chain.py` | Estrutura da chain LCEL |
| `test_router.py` | Lógica de roteamento |
| `test_pqal.py` | Parser PQAL e atalho direto |
| `test_orchestrator.py` | Integração end-to-end (lento, usa Ollama) |
| `test_ui_progress.py` | Helpers de progresso na UI |

### Infraestrutura

| Arquivo | Função |
|---------|--------|
| `docker-compose.yml` | PostgreSQL 16 com pgvector na porta 5432 |
| `init.sql` | Schema + seed executado na primeira subida |
| `.streamlit/config.toml` | `fileWatcherType = "none"` (evita warnings torchvision) |

---

## Pasta `docs/superpowers/`

Documentação gerada durante o desenvolvimento do MVP:

| Caminho | Conteúdo |
|---------|----------|
| `specs/2026-09-12-langchain-clinical-mvp-design.md` | Especificação de arquitetura, decisões de design, requisitos |
| `plans/2026-09-12-langchain-clinical-mvp.md` | Plano de implementação por tarefas |

---

## Pasta `ori_pqal-model-pt/`

Adapter LoRA fine-tuned para **PQAL em português** (respostas sim/não/talvez com contexto científico).

| Arquivo | Função |
|---------|--------|
| `adapter_config.json` | Configuração do adapter PEFT |
| `model.safetensors` | Pesos do adapter |
| `tokenizer.json` | Tokenizer |
| `Modelfile` | Definição para import no Ollama |

Distribuído como **`ori-pqal-model-pt.zip`** (~151 MB, Git LFS). Extraia na raiz do projeto e siga [`ori_pqal-model-pt/README.md`](ori_pqal-model-pt/README.md) para importar no Ollama.

O modelo foi treinado com dataset no formato:

```
Pergunta: [pergunta clínica]?
Contexto: [trecho de artigo/estudo]
→ Resposta: sim/não/talvez + justificativa
```

---

## Roteamento — regras de decisão

O `router.py` aplica regras nesta ordem:

1. **PQAL_SEM_CONTEXTO** nos dados → `llama3.1:8b` (explica formato)
2. **Tool de sistema** usada (buscar_paciente, criar_paciente, etc.) → `llama3.1:8b`
3. **preparar_contexto_pqal** + contexto científico → `ori-pqal-pt`
4. **"Contexto:"** na pergunta do usuário → `ori-pqal-pt`
5. **Fallback LLM** (`llama3.1:8b` classifica) → decisão final

---

## Variáveis de ambiente

Arquivo: `langchain/.env` (copiar de `.env.example`)

```env
DATABASE_URL=postgresql://pqal:pqal@localhost:5432/pqal
OLLAMA_MODEL=ori-pqal-pt
OLLAMA_AGENT_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Como executar

### 1. Pré-requisitos

- Docker Desktop
- Python 3.11+
- [Ollama](https://ollama.com)

### 2. Modelos Ollama

```powershell
ollama pull llama3.1:8b
# ori-pqal-pt: extrair ori-pqal-model-pt.zip e ver ori_pqal-model-pt/README.md
```

### 3. Banco de dados

```powershell
cd langchain
docker compose up -d
```

### 4. Aplicação

```powershell
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

Abra http://localhost:8501

### 5. Testes

```powershell
# rápidos (sem Ollama)
python -m pytest tests/test_router.py tests/test_pqal.py tests/test_escrita.py tests/test_tools.py -v

# completos (inclui integração com Ollama — lento)
python -m pytest tests/ -v
```

---

## Exemplos de uso no chat

### Dados do sistema (llama3.1:8b)

```
Quais pacientes estão disponíveis?
Quais foram os últimos exames do paciente João?
Quais medicamentos o paciente 1 está tomando?
Faça uma análise do estado atual do paciente João.
Cadastre Ana Costa, nascida em 15/05/1980.
Atualize o paciente 1 para o nome João Silva Santos.
Registre glicemia 110 mg/dL para o paciente 2.
```

### PQAL (ori-pqal-pt)

```
Pergunta: Terapia de falta de ar controlada pelo paciente em cuidados paliativos?

Contexto: A falta de ar é um dos sintomas mais angustiantes experimentados por pacientes com câncer avançado...
```

Resposta esperada: `Resposta: sim/não/talvez` + justificativa baseada **somente** no contexto.

---

## Mapa de dependências entre módulos

```
app.py
 ├── ui_progress.py → agent.py → tools/* → db/queries.py → db/connection.py
 ├── router.py
 └── chain.py
      ├── resposta_sistema.py → llama3.1:8b
      └── llm_stream.py → ori-pqal-pt

orchestrator.py → chain.py (API alternativa)
health.py → config.py + Ollama API
```

---

## Licença e limitações (MVP)

- Sem autenticação ou controle de acesso
- Escrita no banco sem confirmação do usuário
- Dados clínicos fictícios para demonstração
- pgvector preparado para embeddings futuros (não usado na chain atual)
