import os
from pathlib import Path
# Removido 'import streamlit as st' daqui para evitar erro na API

def in_streamlit_cloud():
    # Verifica se a aplicação está sendo executada no ambiente do Streamlit Cloud
    # Baseado em variáveis de ambiente definidas pelo Streamlit Cloud
    return "STREAMLIT_SERVER_URL" in os.environ or "STREAMLIT_CLOUD" in os.environ


def get_env_var(key, default=None):
    if in_streamlit_cloud():
        # Apenas tenta importar streamlit DENTRO desta função se for ambiente cloud
        try:
            import streamlit as st
            # No Streamlit Cloud, as variáveis de ambiente são acessadas via st.secrets
            return st.secrets.get(key, default)
        except ImportError:
            # Caso não consiga importar Streamlit, talvez não seja o ambiente Streamlit Cloud
            # ou haja algum problema de setup. Fallback para os.getenv
            return os.getenv(key, default)
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
ENV = get_env_var("ENV").lower() # 'local' é o padrão

# LLM_CLOUD_MODEL_NAME: Nome do modelo para uso em ambiente de nuvem (ex: Hugging Face)
LLM_CLOUD_MODEL_NAME = get_env_var("LLM_CLOUD_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0") # <-- Alterado para TinyLlama
# HF_TOKEN: Token de autenticação para Hugging Face, necessário para modelos privados ou cotas
HF_TOKEN = get_env_var("HF_TOKEN")


# API_BASE_URL: URL base da API FastAPI. Essencial para a comunicação Streamlit <-> API.
# Em ambiente local, será localhost. Em ambiente de nuvem, precisa ser a URL pública da API.
API_BASE_URL = get_env_var("API_BASE_URL", "http://localhost:8000")
# RENDER_API_URL: (Opcional) URL específica para o deploy no Render, caso seja usado.
# Esta variável seria definida no Streamlit Secrets.
RENDER_API_URL = get_env_var("RENDER_API_URL")
