import os
from pathlib import Path
import streamlit as st # Importado para usar st.secrets

def in_streamlit_cloud():
    # Verifica se a aplicação está sendo executada no ambiente do Streamlit Cloud
    # Uma forma comum é verificar a presença de `st.secrets` ou variáveis específicas do ambiente.
    return "streamlit.io" in os.environ.get("STREAMLIT_SERVER_URL", "") or "streamlit.io" in st.__file__


def get_env_var(key, default=None):
    if in_streamlit_cloud():
        # No Streamlit Cloud, as variáveis de ambiente são acessadas via st.secrets
        # st.secrets é um objeto semelhante a um dicionário para segredos
        return st.secrets.get(key, default)
    else:
        # Em ambiente local, carregar variáveis de ambiente de um arquivo .env
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, default)

# Caminhos base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input" # Para uploads temporários de ZIP
TEMP_DIR = DATA_DIR / "temp"   # Para arquivos extraídos do ZIP
LOGS_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "notas.db" # Caminho para o banco de dados SQLite
MODELS_DIR = BASE_DIR / "models" # Para modelos LLM locais (se usados)

# Cria os diretórios se eles não existirem
INPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Variáveis de ambiente híbridas (lidas de .env ou st.secrets)
# ENV: Define o ambiente de execução ('local' ou 'cloud')
ENV = get_env_var("ENV", "local").lower() # 'local' é o padrão

# LLM_CLOUD_MODEL_NAME: Nome do modelo para uso em ambiente de nuvem (ex: Hugging Face)
LLM_CLOUD_MODEL_NAME = get_env_var("LLM_CLOUD_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3")
# HF_TOKEN: Token de autenticação para Hugging Face, necessário para modelos privados ou cotas
HF_TOKEN = get_env_var("HF_TOKEN")

# LLM_LOCAL_MODEL_FILENAME: Nome do arquivo do modelo LLM local (ex: GGUF)
LLM_LOCAL_MODEL_FILENAME = get_env_var("LLM_LOCAL_MODEL_PATH", "llama-2-7b-chat.Q4_K_M.gguf")
# LLM_LOCAL_MODEL_PATH: Caminho completo para o modelo LLM local
LLM_LOCAL_MODEL_PATH = MODELS_DIR / LLM_LOCAL_MODEL_FILENAME

# API_BASE_URL: URL base da API FastAPI. Essencial para a comunicação Streamlit <-> API.
# Em ambiente local, será localhost. Em ambiente de nuvem, precisa ser a URL pública da API.
API_BASE_URL = get_env_var("API_BASE_URL", "http://localhost:8000")
# RENDER_API_URL: (Opcional) URL específica para o deploy no Render, caso seja usado.
# Esta variável seria definida no Streamlit Secrets.
RENDER_API_URL = get_env_var("RENDER_API_URL")