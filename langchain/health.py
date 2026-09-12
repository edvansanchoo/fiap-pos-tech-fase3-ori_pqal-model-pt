import json
import urllib.request
from config import OLLAMA_BASE_URL, OLLAMA_MODEL


def check_ollama_available() -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA_BASE_URL}/api/tags", timeout=3) as resp:
            data = json.loads(resp.read().decode())
            model_names = [m.get("name", "") for m in data.get("models", [])]
            return any(
                name == OLLAMA_MODEL or name == f"{OLLAMA_MODEL}:latest"
                for name in model_names
            )
    except Exception:
        return False
