from collections.abc import Callable
from dataclasses import dataclass

from langchain_classic.agents import AgentExecutor, create_react_agent, create_tool_calling_agent
from agent_callbacks import ToolProgressHandler
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import ChatOllama
from config import OLLAMA_AGENT_MODEL, OLLAMA_BASE_URL
from tools import ALL_TOOLS
from tools.pqal import formatar_contexto_pqal, tem_contexto_pqal


@dataclass
class GatherResult:
    contexto: str
    tools_usadas: list[str]

AGENT_INSTRUCTIONS = """Você é um agente de coleta de dados clínicos.

Sua função é interpretar a solicitação e executar as ferramentas necessárias.
Você NÃO redige a resposta final — apenas coleta dados via tools.

Regras:
1. Use sempre as ferramentas. Nunca invente informações.
2. Escolha a ferramenta conforme a intenção:
   - Listar todos → listar_pacientes_disponiveis
   - Um paciente por nome/ID → buscar_paciente
   - Cadastrar paciente → criar_paciente (nome + data_nascimento)
   - Atualizar paciente → atualizar_paciente (ID + campos a alterar)
   - Exames → buscar_exames / registrar_exame
   - Medicamentos → buscar_medicamentos / registrar_medicamento
   - Prontuário → buscar_prontuario
   - Dados completos do paciente → montar_contexto_paciente
   - PQAL ou pergunta clínica geral → preparar_contexto_pqal (repasse a mensagem INTEIRA do usuário)
   - Ajuda → mostrar_ajuda
3. Se não tiver o ID, use buscar_paciente uma vez e depois a tool de dados.
4. Passe apenas valores necessários (ex: 1, João).
5. Para preparar_contexto_pqal: copie a pergunta original completa, incluindo Pergunta: e Contexto:.
6. Após obter os dados necessários, PARE imediatamente. Não repita a mesma tool.
7. Para ReAct: termine com "Final Answer: coleta concluída"."""

TOOL_CALLING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", AGENT_INSTRUCTIONS),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

REACT_PROMPT = PromptTemplate.from_template(
    AGENT_INSTRUCTIONS
    + """

Ferramentas:
{tools}

Nomes: {tool_names}

Formato:
Thought: ...
Action: ferramenta
Action Input: entrada
Observation: resultado
Thought: dados coletados
Final Answer: coleta concluída

Pergunta: {input}
Thought: {agent_scratchpad}"""
)


def _make_llm() -> ChatOllama:
    return ChatOllama(
        model=OLLAMA_AGENT_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )


def _prefers_tool_calling(model: str) -> bool:
    name = model.lower()
    return any(tag in name for tag in ("3.1", "3.2", "mistral", "qwen", "command-r"))


def _make_executor(use_tool_calling: bool) -> AgentExecutor:
    llm = _make_llm()
    if use_tool_calling:
        agent = create_tool_calling_agent(llm, ALL_TOOLS, TOOL_CALLING_PROMPT)
    else:
        agent = create_react_agent(llm, ALL_TOOLS, REACT_PROMPT)
    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=8,
        return_intermediate_steps=True,
    )


def create_agent_executor() -> AgentExecutor:
    return _make_executor(use_tool_calling=_prefers_tool_calling(OLLAMA_AGENT_MODEL))


def _coletar_pqal_direto(pergunta: str) -> GatherResult | None:
    if not tem_contexto_pqal(pergunta):
        return None
    formatado = formatar_contexto_pqal(pergunta)
    if "PQAL_SEM_CONTEXTO" in formatado:
        return None
    return GatherResult(
        contexto=(
            f"### Tool: preparar_contexto_pqal\n"
            f"**Entrada:** mensagem original do usuário\n\n"
            f"**Dados:**\n{formatado}"
        ),
        tools_usadas=["preparar_contexto_pqal"],
    )


def _notificar_pqal_direto(
    pergunta: str,
    on_tool_progress: Callable[[str, str, object | None], None] | None,
) -> None:
    if not on_tool_progress:
        return
    on_tool_progress("start", "preparar_contexto_pqal", pergunta)
    on_tool_progress("end", "preparar_contexto_pqal", None)


def _formatar_passos_intermediarios(steps: list) -> str:
    if not steps:
        return ""
    vistos: set[tuple[str, str]] = set()
    blocos = []
    for action, observation in steps:
        chave = (action.tool, str(observation))
        if chave in vistos:
            continue
        vistos.add(chave)
        blocos.append(
            f"### Tool: {action.tool}\n"
            f"**Entrada:** {action.tool_input}\n\n"
            f"**Dados:**\n{observation}"
        )
    return "\n\n".join(blocos)


def gather_structured_context(
    pergunta: str,
    on_tool_progress: Callable[[str, str, object | None], None] | None = None,
) -> GatherResult:
    """Etapa 1 da chain: llama3.1 decide e executa tools, retorna dados estruturados."""
    pqal_direto = _coletar_pqal_direto(pergunta)
    if pqal_direto:
        _notificar_pqal_direto(pergunta, on_tool_progress)
        return pqal_direto

    use_tool_calling = _prefers_tool_calling(OLLAMA_AGENT_MODEL)
    callbacks = [ToolProgressHandler(on_tool_progress)] if on_tool_progress else []

    def _invoke(executor: AgentExecutor) -> dict:
        return executor.invoke(
            {"input": pergunta},
            config={"callbacks": callbacks},
        )

    try:
        result = _invoke(_make_executor(use_tool_calling))
    except Exception as exc:
        if not use_tool_calling or "does not support tools" not in str(exc):
            raise
        result = _invoke(_make_executor(False))

    steps = result.get("intermediate_steps", [])
    tools_usadas = list(dict.fromkeys(action.tool for action, _ in steps))
    contexto = _formatar_passos_intermediarios(steps)
    if not contexto:
        contexto = result.get("output", "Nenhum dado foi coletado.")

    if "PQAL_SEM_CONTEXTO" in contexto:
        pqal_direto = _coletar_pqal_direto(pergunta)
        if pqal_direto:
            return pqal_direto

    return GatherResult(contexto=contexto, tools_usadas=tools_usadas)
