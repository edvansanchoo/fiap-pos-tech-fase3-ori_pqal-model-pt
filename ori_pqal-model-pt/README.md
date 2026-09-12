# ori-pqal-pt — Adapter LoRA PQAL (português)

Modelo fine-tuned para **Perguntas com Contexto e Respostas com Limites (PQAL)** em português.  
Responde **sim**, **não** ou **talvez** com justificativa breve, usando somente o contexto científico fornecido.

Base: `unsloth/llama-3-8b-bnb-4bit` (LoRA via PEFT).

## Download dos pesos (~151 MB)

Os arquivos grandes (`model.safetensors`, `tokenizer.json`) não ficam soltos no git — vêm no zip na raiz do repositório:

```powershell
# requer Git LFS instalado
git lfs install
git clone <url-do-repositorio>
cd <repositorio>

# extrair na raiz (cria/sobrescreve ori_pqal-model-pt/)
Expand-Archive -Path ori-pqal-model-pt.zip -DestinationPath . -Force
```

> O zip tem ~151 MB e é servido via **Git LFS** (limite do GitHub: 100 MB por arquivo sem LFS).

---

# Conversão do adapter LoRA para Ollama

Este guia converte o adapter PEFT (`ori_pqal-model-pt`) em um modelo utilizável no Ollama.

## Pré-requisitos

- [Ollama](https://ollama.com) instalado e em execução
- Modelo base baixado:

```powershell
ollama pull llama3:8b
```

## Passos

### 1. Entrar na pasta do modelo

Todos os comandos abaixo devem ser executados dentro de `ori_pqal-model-pt`:

```powershell
cd ori_pqal-model-pt
```

### 2. Renomear o arquivo do adapter

O Ollama espera o arquivo com o nome `model.safetensors`:

```powershell
Rename-Item .\adapter_model.safetensors model.safetensors
```

> Se o arquivo já estiver renomeado, pule este passo.

### 3. Criar o Modelfile

Crie o arquivo `Modelfile` na pasta `ori_pqal-model-pt` com o conteúdo abaixo:

```
FROM llama3:8b

ADAPTER ./model.safetensors

SYSTEM """
Você deve responder exclusivamente com base nas informações fornecidas no contexto.

Regras:
- Não use conhecimento externo.
- Não invente informações.
- Não complemente o contexto com informações que não foram fornecidas.
- Responda somente "sim", "não" ou "talvez", seguido de uma justificativa breve.
- Se o contexto não permitir determinar a resposta, responda "talvez".
"""
```

> O `Modelfile` já está incluído neste repositório com esse conteúdo.

### 4. Criar o modelo no Ollama

Ainda dentro de `ori_pqal-model-pt`:

```powershell
ollama create ori-pqal-pt -f Modelfile
```

> **Importante:** o comando precisa ser executado na mesma pasta onde estão o `Modelfile` e o `model.safetensors`. Executar na pasta pai causa o erro `no Modelfile or safetensors files found`.

### 5. Usar o modelo

```powershell
ollama run ori-pqal-pt
```

No assistente clínico (`langchain/`), configure no `.env`:

```env
OLLAMA_MODEL=ori-pqal-pt
```

## Estrutura da pasta

```
ori_pqal-model-pt/
├── adapter_config.json
├── model.safetensors      # pesos do adapter LoRA (~160 MB)
├── Modelfile              # definição para o Ollama
├── tokenizer.json
├── tokenizer_config.json
└── README.md              # este arquivo
```

## Formato de uso (PQAL)

```
Pergunta: [sua pergunta clínica]?

Contexto: [trecho do artigo ou estudo científico]
```

Resposta esperada:

```
Resposta: sim|não|talvez

[justificativa breve baseada no contexto]
```
