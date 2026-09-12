from db import queries

MENSAGEM_AJUDA = """Posso ajudar de duas formas:

**1. Dados clínicos do banco** (pacientes de exemplo)
- "Quais pacientes estão disponíveis?"
- "Quais foram os últimos exames do paciente João?"
- "Quais medicamentos o paciente 1 está tomando?"
- "Faça uma análise do estado atual do paciente João."
- "Cadastre o paciente Ana Costa, nascida em 15/05/1980."
- "Atualize o paciente 1 para o nome João Silva Santos."
- "Registre glicemia 110 mg/dL para o paciente 2."

**2. Perguntas de pesquisa clínica (PQAL)** — formato sim/não/talvez
Envie pergunta + contexto:
```
Pergunta: Sua pergunta aqui?

Contexto: Trecho do artigo ou estudo...
```
O modelo ori-pqal-pt responde somente com base no contexto fornecido."""


def formatar_lista_pacientes() -> str:
    pacientes = queries.listar_pacientes()
    if not pacientes:
        return "Nenhum paciente cadastrado no banco."

    linhas = ["Pacientes disponíveis:", ""]
    for p in pacientes:
        idade = queries.calcular_idade(p["data_nascimento"])
        linhas.append(f"- **{p['id']}** — {p['nome']} ({idade} anos)")
    linhas.append("")
    linhas.append("Use o nome ou ID nas perguntas (ex: paciente João, paciente 1).")
    return "\n".join(linhas)
