# app/config.py
import os
from pathlib import Path

def in_streamlit_cloud():
    try:
        import streamlit as st
        return hasattr(st, "secrets") and "ENV" in st.secrets
    except ImportError:
        return False

def get_env_var(key, default=None):
    if in_streamlit_cloud():
        import streamlit as st
        return st.secrets.get(key, default)
    else:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, default)

# Caminhos base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
TEMP_DIR = DATA_DIR / "temp"
LOGS_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "notas.db"
MODELS_DIR = BASE_DIR / "models"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Variáveis de ambiente híbridas
ENV = get_env_var("ENV", "local").lower()
LLM_CLOUD_MODEL_NAME = get_env_var("LLM_CLOUD_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3")
HF_TOKEN = get_env_var("HF_TOKEN")
LLM_LOCAL_MODEL_FILENAME = get_env_var("LLM_LOCAL_MODEL_PATH", "llama-2-7b-chat.Q4_K_M.gguf")
LLM_LOCAL_MODEL_PATH = MODELS_DIR / LLM_LOCAL_MODEL_FILENAME
API_BASE_URL = get_env_var("API_BASE_URL", "http://localhost:8000")

