import os
from pathlib import Path


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

# Variáveis obrigatórias para nuvem
ENV = "cloud"
HF_TOKEN = get_env_var("HF_TOKEN")
API_BASE_URL = get_env_var("API_BASE_URL")
LLM_CLOUD_MODEL_NAME = get_env_var("LLM_CLOUD_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# LLM_CLOUD_MODEL_NAME: Nome do modelo para uso em ambiente de nuvem (ex: Hugging Face)
LLM_CLOUD_MODEL_NAME = get_env_var("LLM_CLOUD_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0") # <-- Alterado para TinyLlama
# HF_TOKEN: Token de autenticação para Hugging Face, necessário para modelos privados ou cotas
HF_TOKEN = get_env_var("HF_TOKEN")

API_BASE_URL = get_env_var("API_BASE_URL", "http://localhost:8000")
RENDER_API_URL = get_env_var("RENDER_API_URL")
