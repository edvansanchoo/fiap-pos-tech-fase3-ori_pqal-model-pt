import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pqal:pqal@localhost:5432/pqal")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ori-pqal-pt")
OLLAMA_AGENT_MODEL = os.getenv("OLLAMA_AGENT_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
