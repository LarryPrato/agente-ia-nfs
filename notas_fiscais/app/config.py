import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Caminhos base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent # Vai para a raiz do projeto

# Diretórios de dados
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
TEMP_DIR = DATA_DIR / "temp"
LOGS_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "notas.db"
MODELS_DIR = BASE_DIR / "models"

# Garante que os diretórios existem
INPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Configurações do ambiente (cloud/local)
ENV = os.getenv("ENV", "local").lower() # Default para 'local'

# Configurações do LLM em nuvem
LLM_CLOUD_MODEL_NAME = os.getenv("LLM_CLOUD_MODEL_NAME", "google/flan-t5-base")
# LLM_CLOUD_API_KEY = os.getenv("LLM_CLOUD_API_KEY") # Se necessário para algum LLM específico

# Configurações do LLM local (LlamaCpp)
LLM_LOCAL_MODEL_FILENAME = os.getenv("LLM_LOCAL_MODEL_PATH", "llama-2-7b-chat.Q4_K_M.gguf")
LLM_LOCAL_MODEL_PATH = MODELS_DIR / LLM_LOCAL_MODEL_FILENAME

# URL base da API (para o Streamlit consumir a API)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Exemplo de uso (apenas para debug se rodar este arquivo diretamente)
if __name__ == "__main__":
    print(f"Ambiente: {ENV}")
    print(f"Caminho do DB: {DB_PATH}")
    print(f"Diretório de Input: {INPUT_DIR}")
    print(f"Diretório de Logs: {LOGS_DIR}")
    print(f"Diretório de Modelos: {MODELS_DIR}")
    if ENV == "cloud":
        print(f"Modelo Cloud: {LLM_CLOUD_MODEL_NAME}")
    else:
        print(f"Modelo Local: {LLM_LOCAL_MODEL_PATH}")
    print(f"API Base URL: {API_BASE_URL}")