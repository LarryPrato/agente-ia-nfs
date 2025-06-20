# app/config.py
import streamlit as st
from pathlib import Path

def get_env_var(key, default=None):
    return st.secrets.get(key, default)

# Caminhos base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "notas.db"
INPUT_DIR = BASE_DIR / "data" / "input"
TEMP_DIR = BASE_DIR / "data" / "temp"
LOGS_DIR = BASE_DIR / "data" / "logs"
MODELS_DIR = BASE_DIR / "models"

# Criar pastas se não existirem
for d in [INPUT_DIR, TEMP_DIR, LOGS_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Variáveis obrigatórias (vêm de st.secrets no Streamlit Cloud)
ENV = "cloud"
HF_TOKEN = get_env_var("HF_TOKEN")
LLM_CLOUD_MODEL_NAME = get_env_var("LLM_CLOUD_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
API_BASE_URL = get_env_var("API_BASE_URL")  # ← Obrigatório informar nos secrets
RENDER_API_URL = get_env_var("RENDER_API_URL")  # ← opcional, você pode remover se não usar
