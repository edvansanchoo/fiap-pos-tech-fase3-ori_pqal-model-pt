import json
import urllib.request
from config import OLLAMA_AGENT_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL


def _listar_modelos() -> list[str]:
    with urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=3) as resp:
        data = json.loads(resp.read().decode())
        return [m.get("name", "") for m in data.get("models", [])]


def _modelo_disponivel(modelo: str, model_names: list[str]) -> bool:
    return modelo in model_names or f"{modelo}:latest" in model_names


def check_ollama_available() -> bool:
    try:
        model_names = _listar_modelos()
        return (
            _modelo_disponivel(OLLAMA_MODEL, model_names)
            and _modelo_disponivel(OLLAMA_AGENT_MODEL, model_names)
        )
    except Exception:
        return False


def check_modelos() -> dict[str, bool]:
    try:
        model_names = _listar_modelos()
        return {
            "ori_pqal": _modelo_disponivel(OLLAMA_MODEL, model_names),
            "agente": _modelo_disponivel(OLLAMA_AGENT_MODEL, model_names),
        }
    except Exception:
        return {"ori_pqal": False, "agente": False}
