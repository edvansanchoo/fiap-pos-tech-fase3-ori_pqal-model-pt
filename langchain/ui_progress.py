import queue
import threading
import time
from collections.abc import Callable

from agent import GatherResult, gather_structured_context


def formatar_entrada_tool(entrada: object) -> str:
    texto = str(entrada).strip()
    return texto if len(texto) <= 80 else texto[:77] + "..."


def montar_texto_tools(linhas: list[str], concluidas: list[str]) -> str:
    partes = list(linhas)
    if concluidas:
        partes.append(f"✓ Concluídas: `{'`, `'.join(concluidas)}`")
    return "\n\n".join(partes) if partes else "_Aguardando agente..._"


def gather_com_progresso_tempo_real(
    pergunta: str,
    on_atualizar: Callable[[str], None],
) -> GatherResult:
    """Executa o agente em thread e atualiza a UI na thread principal."""
    fila: queue.Queue = queue.Queue()
    resultado: dict[str, GatherResult] = {}

    def on_tool_progress(evento: str, nome: str, dado: object | None) -> None:
        fila.put(("progress", evento, nome, dado))

    def worker() -> None:
        try:
            resultado["coleta"] = gather_structured_context(
                pergunta,
                on_tool_progress=on_tool_progress,
            )
            fila.put(("done", None, None, None))
        except Exception as exc:
            fila.put(("error", str(exc), None, None))

    linhas: list[str] = []
    concluidas: list[str] = []

    def render() -> None:
        on_atualizar(montar_texto_tools(linhas, concluidas))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    render()

    while True:
        try:
            kind, evento, nome, dado = fila.get(timeout=0.05)
        except queue.Empty:
            render()
            if not thread.is_alive():
                break
            time.sleep(0.05)
            continue

        if kind == "error":
            raise RuntimeError(evento)
        if kind == "done":
            break

        if evento == "start":
            linhas.append(f"⏳ Executando `{nome}` — `{formatar_entrada_tool(dado)}`")
        elif evento == "end":
            linhas.append(f"✓ `{nome}` finalizada")
            if nome not in concluidas:
                concluidas.append(nome)
        render()

    thread.join(timeout=1)
    if "coleta" not in resultado:
        raise RuntimeError("Coleta de dados não retornou resultado.")
    return resultado["coleta"]
