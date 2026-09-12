from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
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
