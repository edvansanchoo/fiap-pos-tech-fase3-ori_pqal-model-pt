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
