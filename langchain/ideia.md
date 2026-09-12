3. Agora vem a parte interessante: banco de dados

Suponha que você tenha SQL Server:

PACIENTE
----------------
id
nome
data_nascimento

PRONTUARIO
----------------
id
paciente_id
data
descricao

EXAME
----------------
id
paciente_id
data
tipo
resultado

MEDICAMENTO
----------------
id
paciente_id
medicamento
dose
data_inicio

O usuário pergunta:

"Quais foram os últimos exames do paciente João?"

Você não deveria colocar todos os prontuários no prompt.

O LangChain pode trabalhar com ferramentas que consultam dados externos. A própria documentação define tools justamente como funções que permitem ao agente consultar bancos externos e executar ações.

Por exemplo:

from langchain.tools import tool

@tool
def buscar_exames(paciente_id: int) -> str:
    """
    Busca os exames mais recentes de um paciente.
    """

    # consulta SQL aqui

    return """
    2026-09-01 - Hemograma:
    Hemoglobina: 13.8

    2026-08-20 - Glicemia:
    Resultado: 95 mg/dL
    """

Agora o LLM possui uma ferramenta:

buscar_exames()
4. O fluxo fica assim

Usuário:

Quais foram os últimos exames do paciente 123?

LangChain:

Pergunta
   ↓
ori-pqal
   ↓
"Preciso consultar os exames"
   ↓
buscar_exames(123)
   ↓
SQL Server
   ↓
resultado
   ↓
ori-pqal
   ↓
resposta

Isso é exatamente o conceito de LLM + tools do LangChain.

5. Mas eu faria uma pequena mudança no seu projeto

Como estamos falando de prontuários, eu evitaria deixar o LLM gerar SQL livremente.

Por exemplo, eu não começaria permitindo:

LLM → "SELECT * FROM qualquer_tabela"

É muito mais seguro criar ferramentas específicas:

buscar_paciente()

buscar_prontuario()

buscar_exames()

buscar_medicamentos()

buscar_consultas()

buscar_sinais_vitais()

Assim você controla exatamente o que o modelo pode acessar.

Por exemplo:

@tool
def buscar_prontuario(paciente_id: int) -> str:
    """Retorna o histórico do prontuário do paciente."""
    
    # SQL controlado pela aplicação
    ...
6. E aí entra a "contextualização com informações atualizadas"

Esse é provavelmente o ponto mais importante do seu trabalho.

Imagine:

Banco
Paciente: João
Idade: 68

Última consulta:
10/09/2026

Pressão:
145/90

Medicamentos:
Medicamento A - 10mg

Último exame:
Glicemia = 132 mg/dL

O usuário pergunta:

"Faça uma análise do estado atual do paciente."

O LangChain coleta:

Paciente
+
Prontuário
+
Exames
+
Medicamentos
+
Última consulta

E constrói:

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

Depois envia para o seu modelo:

SYSTEM:
Você é um assistente de análise de informações clínicas.

Utilize exclusivamente os dados fornecidos no contexto.

Não invente informações.
Não utilize conhecimento externo para preencher informações ausentes.

CONTEXTO:
...

PERGUNTA:
Faça uma análise do estado atual do paciente.

E:

              Banco
                │
                ▼
         Dados atualizados
                │
                ▼
          LangChain
                │
                ▼
        Contexto estruturado
                │
                ▼
            ori-pqal
                │
                ▼
             resposta