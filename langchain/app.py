import streamlit as st
from chain import stream_resposta_chain
from router import classificar_roteamento, legenda_motivo
from ui_progress import gather_com_progresso_tempo_real
from db.connection import check_db_connection
from db import queries
from config import OLLAMA_AGENT_MODEL, OLLAMA_MODEL
from health import check_modelos, check_ollama_available

st.set_page_config(page_title="Assistente Clínico PQAL", page_icon="🏥", layout="wide")
st.title("Assistente Clínico PQAL")
st.caption(
    f"Chain: {OLLAMA_AGENT_MODEL} (tools + dados) | {OLLAMA_MODEL} (só PQAL) | PostgreSQL/pgvector"
)

SUGESTOES = [
    "Quais pacientes estão disponíveis?",
    "Quais foram os últimos exames do paciente João?",
    "Quais medicamentos o paciente 1 está tomando?",
    "Faça uma análise do estado atual do paciente João.",
    "ajuda",
]


def _processar_pergunta(prompt: str) -> str:
    with st.status("Processando pergunta...", expanded=True) as status:
        st.markdown(f"**Etapa 1/3** — Agente `{OLLAMA_AGENT_MODEL}` analisando e executando tools...")
        tools_area = st.empty()

        coleta = gather_com_progresso_tempo_real(
            prompt,
            on_atualizar=tools_area.markdown,
        )

        st.markdown("**Etapa 2/3** — Roteamento da pergunta...")
        roteamento = classificar_roteamento(prompt, coleta.contexto, coleta.tools_usadas)
        modelo = OLLAMA_MODEL if roteamento.usar_ori_pqal else OLLAMA_AGENT_MODEL
        st.markdown(
            f"✓ Destino: **`{modelo}`** — {legenda_motivo(roteamento.motivo)}"
        )

        entrada = {
            "pergunta": prompt,
            "contexto": coleta.contexto,
            "tools_usadas": coleta.tools_usadas,
            "usar_ori_pqal": roteamento.usar_ori_pqal,
            "motivo_roteamento": roteamento.motivo,
            "modelo_resposta": modelo,
            "motivo_legenda": legenda_motivo(roteamento.motivo),
        }

        st.markdown(f"**Etapa 3/3** — Gerando resposta com `{modelo}`...")
        status.update(label="Processamento concluído", state="complete", expanded=False)

    return st.write_stream(stream_resposta_chain(entrada))


with st.sidebar:
    st.header("Status")
    db_ok = check_db_connection()
    modelos = check_modelos()
    ollama_ok = check_ollama_available()
    st.write("🟢 Banco de dados" if db_ok else "🔴 Banco indisponível — execute `docker compose up -d`")
    st.write(
        f"🟢 Agente ({OLLAMA_AGENT_MODEL})"
        if modelos["agente"]
        else f"🔴 Modelo agente não encontrado — `ollama pull {OLLAMA_AGENT_MODEL}`"
    )
    st.write(
        f"🟢 Análise/PQAL ({OLLAMA_MODEL})"
        if modelos["ori_pqal"]
        else f"🔴 Modelo {OLLAMA_MODEL} não encontrado"
    )

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
        st.error(
            f"Ollama indisponível ou modelos não encontrados. "
            f"Necessário: {OLLAMA_AGENT_MODEL} e {OLLAMA_MODEL}."
        )
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            resposta = _processar_pergunta(prompt)
        except Exception as exc:
            st.error(f"Não foi possível processar a pergunta: {exc}")
            st.stop()

    st.session_state.messages.append({"role": "assistant", "content": resposta})
