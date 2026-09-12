# ori-pqal-pt — Adapter LoRA PQAL (português)

Modelo fine-tuned para **Perguntas com Contexto e Respostas com Limites (PQAL)** em português.  
Responde **sim**, **não** ou **talvez** com justificativa breve, usando somente o contexto científico fornecido.

Base: `unsloth/llama-3-8b-bnb-4bit` (LoRA via PEFT).

## Download (~151 MB)

O modelo completo está em **`ori-pqal-model-pt.zip`** na raiz do repositório (Git LFS):

```powershell
git lfs install
git clone <url-do-repositorio>
cd <repositorio>
Expand-Archive -Path ori-pqal-model-pt.zip -DestinationPath . -Force
```

Isso cria a pasta `ori_pqal-model-pt/` com todos os arquivos.

## Conversão para Ollama

### Pré-requisitos

- [Ollama](https://ollama.com) instalado
- `ollama pull llama3:8b`

### Passos

```powershell
cd ori_pqal-model-pt
ollama create ori-pqal-pt -f Modelfile
ollama run ori-pqal-pt
```

No `langchain/.env`:

```env
OLLAMA_MODEL=ori-pqal-pt
```

> Execute `ollama create` **dentro** de `ori_pqal-model-pt/` (onde estão `Modelfile` e `model.safetensors`).

## Formato PQAL

```
Pergunta: [sua pergunta clínica]?

Contexto: [trecho do artigo ou estudo]
```

Resposta: `sim` | `não` | `talvez` + justificativa.
