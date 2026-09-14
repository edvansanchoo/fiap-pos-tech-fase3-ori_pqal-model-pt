# Roteiro de Apresentação — Tech Challenge Fase 3

**Assistente Clínico PQAL | 3 apresentadores | ~15 minutos**

---

## Visão geral da divisão


| Parte | Apresentador | Tempo  | Foco                                                   |
| ----- | ------------ | ------ | ------------------------------------------------------ |
| **1** | Pessoa A     | ~5 min | Fine-tuning: dataset, tradução EN→PT, treinamento LoRA |
| **2** | Pessoa B     | ~4 min | Conversão do adapter para Ollama                       |
| **3** | Pessoa C     | ~6 min | Sistema LangChain, demo e requisitos do desafio        |


### Abertura conjunta (30 s — qualquer um)

> "Somos [nomes]. Vamos apresentar o Tech Challenge da Fase 3: um assistente clínico em português, com LLM fine-tuned para PQAL, integrado ao LangChain e a um banco de prontuários. A apresentação tem três partes: treinamento do modelo, deploy no Ollama e demonstração do sistema."

---



## PARTE 1 — Fine-tuning do modelo (Pessoa A)

**Requisito atendido:** *Fine-tuning de LLM com dados médicos* (item 1 do PDF)

### 1.1 Contexto e problema (45 s)

**Fala sugerida:**

> "O hospital precisa de um assistente que responda perguntas clínicas com base em evidência científica, sem inventar informação. Para isso, escolhemos o formato **PQAL** — Perguntas com Contexto e Respostas com Limites: o modelo só pode responder **sim**, **não** ou **talvez**, com justificativa baseada exclusivamente no contexto fornecido.
>
> Como base de dados usamos o **PubMedQA** (PQAL), sugerido no próprio Tech Challenge: perguntas clínicas com contexto de publicações médicas e resposta fundamentada."

**Mostrar na tela:** slide com o desafio do hospital + link PubMedQA.

---



### 1.2 Base de dados original (1 min)

**Fala sugerida:**

> "O arquivo `fine-tunning/ori_pqal.json` contém milhares de exemplos em inglês. Cada registro tem:
>
> - uma **pergunta** (`QUESTION`);
> - **contextos** científicos (`CONTEXTS`);
> - a **decisão final** (`final_decision`: yes/no/maybe);
> - a **justificativa** (`LONG_ANSWER`).
>
> Exemplo: a pergunta sobre mitocôndrias e morte celular programada vem com dois parágrafos de contexto e resposta 'yes'."

**Mostrar na tela:** trecho de `fine-tunning/ori_pqal.json` (1 exemplo).

---



### 1.3 Conversão EN → PT-BR (1 min 30 s)

**Fala sugerida:**

> "O modelo precisa operar em português para o contexto brasileiro. Criamos o script `fine-tunning/translate_pqal.py`, que:
>
> 1. Lê o dataset em formato JSONL (instruction / input / output);
> 2. Traduz **pergunta** e **contexto** separadamente;
> 3. Mantém o cabeçalho `Resposta: sim/não/talvez` e traduz só a justificativa;
> 4. Usa **Google Translate** e **MyMemory** como fallback;
> 5. Suporta **retomada** — se a tradução parar, continua do último registro;
> 6. Divide textos longos em blocos de até 4.500 caracteres.
>
> O resultado é o `fine-tunning/ori_pqal_pt-br.json`, com a mesma estrutura, em português."

**Mostrar na tela:** lado a lado EN (`ori_pqal.json`) vs PT (`ori_pqal_pt-br.json`).

**Destaque técnico:**

> "Isso atende ao requisito de **preprocessing e curadoria**: adaptamos um dataset público médico ao nosso idioma e formato de treino."

---



### 1.4 Preparação para treino — formato Alpaca (1 min)

**Fala sugerida:**

> "No notebook `fine-tunning/fine-tunning.ipynb`, a função `pqal_to_alpaca()` converte cada registro para o formato de instrução:
>
> - **Instruction:** 'Com base no contexto científico fornecido, responda com sim, não ou talvez e justifique brevemente.'
> - **Input:** `Pergunta: ...` + `Contexto: ...`
> - **Output:** `Resposta: sim/não/talvez` + justificativa
>
> As decisões são mapeadas: yes → sim, no → não, maybe → talvez.
>
> O prompt final segue o template **Alpaca**, padrão para fine-tuning supervisionado."

**Mostrar na tela:** diagrama do fluxo:

```
ori_pqal.json → translate_pqal.py → ori_pqal_pt-br.json → pqal_to_alpaca() → pqal_train_pt-br.jsonl
```

---



### 1.5 Treinamento LoRA (1 min 30 s)

**Fala sugerida:**

> "Para o fine-tuning usamos:
>
> - **Modelo base:** `unsloth/llama-3-8b-bnb-4bit` (LLaMA 3 8B em 4 bits);
> - **Técnica:** LoRA via PEFT/Unsloth — treinamos só um adapter leve (~151 MB), não o modelo inteiro;
> - **Hiperparâmetros LoRA:** rank r=16, alpha=16, módulos q/k/v/o e gate/up/down;
> - **Treino:** SFTTrainer, 400 steps, batch 2, gradient accumulation 4, learning rate 2e-4, max_seq_length 2048.
>
> O treinamento rodou no **Google Colab** com GPU. Ao final, salvamos o adapter em `ori_pqal-model-pt/` com `model.save_pretrained()`.
>
> Testamos com um exemplo de vacina contra gripe e validamos que o modelo responde no formato PQAL esperado."

**Mostrar na tela:** células principais do notebook + saída de inferência de teste.

**Encerramento da Parte 1:**

> "Entregamos o pipeline de fine-tuning, dataset traduzido e modelo LoRA especializado em PQAL em português. Agora [Pessoa B] mostra como colocar esse modelo em produção local com Ollama."

---



## PARTE 2 — Conversão para Ollama (Pessoa B)

**Requisito atendido:** disponibilizar a LLM customizada para uso no assistente (item 2 do PDF)

### 2.1 Por que Ollama? (30 s)

**Fala sugerida:**

> "O adapter LoRA não roda sozinho — precisa do modelo base LLaMA 3 8B. O **Ollama** permite rodar localmente, sem API externa, integrando o adapter ao modelo base de forma simples."

---



### 2.2 Estrutura do pacote (45 s)

**Fala sugerida:**

> "O pacote `ori_pqal-model-pt/` contém:
>
> - `adapter_config.json` — configuração PEFT;
> - `model.safetensors` — pesos do adapter (~160 MB);
> - `tokenizer.json` e `tokenizer_config.json`;
> - `Modelfile` — definição para o Ollama.
>
> Como o arquivo passa de 100 MB, distribuímos via **Git LFS** no zip `ori-pqal-model-pt.zip`."

**Mostrar na tela:** árvore de arquivos do `ori_pqal-model-pt/README.md`.

---



### 2.3 Passo a passo da conversão (2 min 30 s)

**Fala sugerida (demonstrar no terminal ou slides com comandos):**

> **Pré-requisito 1:** Ollama instalado e rodando.
>
> **Pré-requisito 2:** baixar o modelo base:
>
> ```powershell
> ollama pull llama3:8b
> ```
>
> **Passo 1:** extrair o zip e entrar na pasta:
>
> ```powershell
> Expand-Archive -Path ori-pqal-model-pt.zip -DestinationPath . -Force
> cd ori_pqal-model-pt
> ```
>
> **Passo 2:** garantir que o adapter está como `model.safetensors` (o Ollama espera esse nome):
>
> ```powershell
> Rename-Item .\adapter_model.safetensors model.safetensors
> ```
>
> **Passo 3:** o `Modelfile` define o modelo base + adapter + prompt de sistema:
>
> ```
> FROM llama3:8b
> ADAPTER ./model.safetensors
> SYSTEM """Você deve responder exclusivamente com base no contexto...
> Responda somente sim, não ou talvez..."""
> ```
>
> **Passo 4:** criar o modelo no Ollama — **importante:** executar dentro da pasta:
>
> ```powershell
> ollama create ori-pqal-pt -f Modelfile
> ```
>
> **Passo 5:** testar:
>
> ```powershell
> ollama run ori-pqal-pt
> ```
>
> **Passo 6:** no assistente LangChain, configurar no `.env`:
>
> ```env
> OLLAMA_MODEL=ori-pqal-pt
> ```

**Mostrar na tela:** terminal com `ollama create` e um teste PQAL manual.

---



### 2.4 Formato de uso PQAL (30 s)

**Fala sugerida:**

> "O modelo espera:
>
> ```
> Pergunta: [pergunta clínica]?
> Contexto: [trecho do artigo]
> ```
>
> E responde:
>
> ```
> Resposta: sim|não|talvez
> [justificativa breve]
> ```
>
> O SYSTEM prompt no Modelfile reforça: sem conhecimento externo, sem inventar, e 'talvez' quando o contexto não permite decidir."

**Encerramento da Parte 2:**

> "Com o `ori-pqal-pt` no Ollama, o modelo fine-tuned está pronto para o assistente. [Pessoa C] demonstra o sistema completo."

---



## PARTE 3 — Sistema e funcionalidades (Pessoa C)

**Requisitos atendidos:** *Assistente com LangChain* (item 2), *Segurança/validação* (item 3), *Organização do código* (item 4)

### 3.1 Arquitetura geral (1 min)

**Fala sugerida:**

> "O assistente está em `langchain/` e combina:
>
> - **Streamlit** — interface de chat;
> - **PostgreSQL + pgvector** — prontuários, exames, medicamentos;
> - **Dois modelos Ollama:**
>   - `llama3.1:8b` — agente que interpreta perguntas e executa tools;
>   - `ori-pqal-pt` — respostas PQAL com contexto científico.
>
> O fluxo tem **3 etapas**, visíveis na UI em tempo real."

**Mostrar na tela:** diagrama do README:

```
Pergunta → Etapa 1 (agent.py) → Etapa 2 (router.py) → Etapa 3 (chain.py)
                                              ├─ llama3.1:8b (dados do sistema)
                                              └─ ori-pqal-pt (PQAL)
```

---



### 3.2 Etapa 1 — Coleta com LangChain Tools (1 min 30 s)

**Fala sugerida:**

> "Na **Etapa 1**, o agente `llama3.1:8b` usa **12 LangChain tools** para consultar e atualizar o banco — sem chamar LLM dentro das tools.
>
> **Leitura:** listar pacientes, buscar paciente, exames, medicamentos, prontuário, montar contexto clínico completo.
>
> **Escrita:** criar/atualizar paciente, registrar exame, registrar medicamento.
>
> **PQAL:** `preparar_contexto_pqal` extrai pergunta e contexto.
>
> Se o usuário já envia `Pergunta:` + `Contexto:` na mensagem, há um atalho direto — sem passar pelo agente.
>
> O progresso das tools aparece em tempo real na interface."

**Demo sugerida (ao vivo ou gravada):**

> "Quais foram os últimos exames do paciente João?"

**Mostrar:** Etapa 1 executando `buscar_paciente` + `buscar_exames`.

---



### 3.3 Etapa 2 — Roteamento inteligente (1 min)

**Fala sugerida:**

> "O `router.py` decide qual modelo gera a resposta final:
>
> 1. PQAL sem contexto → `llama3.1:8b` (explica o formato);
> 2. Tools de sistema usadas → `llama3.1:8b` (formata dados do banco);
> 3. PQAL com contexto científico → `ori-pqal-pt`;
> 4. 'Contexto:' na pergunta → `ori-pqal-pt`;
> 5. Fallback: o próprio agente classifica.
>
> Isso garante que o modelo fine-tuned só é usado quando faz sentido — economia e precisão."

**Mostrar na tela:** sidebar com status (banco, Ollama, modelos) + Etapa 2 na UI.

---



### 3.4 Etapa 3 — Geração da resposta (1 min)

**Fala sugerida:**

> "Na **Etapa 3**:
>
> - Para dados do sistema: `resposta_sistema.py` formata a resposta com `llama3.1:8b`;
> - Para PQAL: `chain.py` envia o prompt ao `ori-pqal-pt` com streaming token a token.
>
> A chain LCEL é `clinical_chain = RunnableLambda(run_clinical_chain)` — orquestração modular em Python."

---



### 3.5 Demonstrações práticas (2 min)



#### Demo 1 — Dados do sistema

> "Faça uma análise do estado atual do paciente João."

**Fala durante a demo:**

> "O agente monta contexto clínico agregando consulta, exames, medicamentos e prontuário. A resposta cita os dados retornados das tools — **explainability**: a fonte são os registros do banco."



#### Demo 2 — PQAL com contexto científico

```
Pergunta: Terapia de falta de ar controlada pelo paciente em cuidados paliativos?

Contexto: A falta de ar é um dos sintomas mais angustiantes experimentados por pacientes com câncer avançado...
```

**Fala durante a demo:**

> "Aqui o roteador escolhe `ori-pqal-pt`. A resposta vem no formato sim/não/talvez, fundamentada só no contexto — exatamente o que treinamos na Parte 1."



#### Demo 3 — Escrita (opcional, se houver tempo)

> "Registre glicemia 110 mg/dL para o paciente 2."

---



### 3.6 Segurança, validação e limitações (1 min)

**Fala sugerida (alinhado ao item 3 do PDF):**

> "Implementamos **limites de atuação**:
>
> - O modelo PQAL não usa conhecimento externo — só o contexto fornecido;
> - Roteamento separa consultas clínicas-evidência de operações no prontuário;
> - As tools mostram quais dados foram consultados — rastreabilidade na UI;
> - O SYSTEM prompt do Ollama reforça: não prescrever, não inventar.
>
> **Limitações do MVP** (transparência para o avaliador):
>
> - Sem autenticação;
> - Escrita no banco sem confirmação humana;
> - Dados fictícios para demonstração;
> - Logging estruturado em arquivo ainda é evolução futura.
>
> Em produção, adicionaríamos auditoria completa, validação humana obrigatória para condutas e anonimização real de dados hospitalares."

---



### 3.7 Organização do código e entregáveis (45 s)

**Fala sugerida:**

> "O repositório está modularizado:
>
> - `fine-tunning/` — pipeline de treino;
> - `ori_pqal-model-pt/` — modelo + guia Ollama;
> - `langchain/` — app, agent, router, chain, tools, db, testes.
>
> O README traz instruções completas: Docker, Ollama, `.env`, Streamlit e pytest.
>
> **Entregáveis do Tech Challenge:**
>
> - Código de fine-tuning e integração LangChain;
> - Dataset sintético/traduzido (PubMedQA);
> - Diagrama de fluxo no README;
> - Este vídeo demonstrando treinamento, deploy e fluxo automatizado."

---



### Encerramento conjunto (30 s)

**Fala sugerida (qualquer um):**

> "Resumindo: fine-tuned um LLaMA 3 8B para PQAL em português com PubMedQA traduzido; deployamos no Ollama como `ori-pqal-pt`; e integramos ao LangChain com roteamento entre agente e modelo especializado, consultando prontuários em PostgreSQL. Obrigado — perguntas?"

---



## Checklist — requisitos do PDF


| Requisito Tech Challenge               | Onde é coberto na apresentação                   |
| -------------------------------------- | ------------------------------------------------ |
| Fine-tuning com dados médicos          | Parte 1 (PubMedQA/PQAL)                          |
| Preprocessing e curadoria              | Parte 1 (tradução + formato Alpaca)              |
| LangChain + LLM customizada            | Partes 2 e 3                                     |
| Consultas em base estruturada          | Parte 3 (12 tools + PostgreSQL)                  |
| Contextualização com dados do paciente | Parte 3 (demo João + `montar_contexto_paciente`) |
| Limites de atuação                     | Parte 3 (PQAL + roteamento + limitações MVP)     |
| Explainability                         | Parte 3 (tools visíveis + fonte no banco)        |
| Código modular + README                | Parte 3                                          |
| Vídeo ≤ 15 min                         | 5 + 4 + 6 min                                    |


---



## Dicas de produção

1. **Gravação:** Parte 1 com slides + notebook; Parte 2 com terminal; Parte 3 com Streamlit ao vivo.
2. **Transições:** cada pessoa termina citando o nome do próximo apresentador.
3. **Backup:** se Ollama falhar na demo, mostrar gravação curta da Etapa 3.
4. **LangGraph:** o PDF menciona LangGraph; o projeto usa **AgentExecutor + chain LCEL**. Se perguntarem, diga que a orquestração em 3 etapas cobre o mesmo papel de fluxo automatizado.

---



## Referências no repositório


| Arquivo / pasta                       | Conteúdo                         |
| ------------------------------------- | -------------------------------- |
| `fine-tunning/translate_pqal.py`      | Script de tradução EN→PT-BR      |
| `fine-tunning/fine-tunning.ipynb`     | Notebook de fine-tuning LoRA     |
| `fine-tunning/ori_pqal.json`          | Dataset original (inglês)        |
| `fine-tunning/ori_pqal_pt-br.json`    | Dataset traduzido                |
| `ori_pqal-model-pt/README.md`         | Guia de conversão para Ollama    |
| `langchain/app.py`                    | Interface Streamlit              |
| `langchain/agent.py`                  | Etapa 1 — coleta com tools       |
| `langchain/router.py`                 | Etapa 2 — roteamento             |
| `langchain/chain.py`                  | Etapa 3 — geração de resposta    |
| `README.md`                           | Documentação completa do projeto |
| `8IADT - Fase 3 - Tech challenge.pdf` | Requisitos oficiais da Fase 3    |


