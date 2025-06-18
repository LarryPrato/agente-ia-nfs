import sys
from pathlib import Path
import subprocess
import os

# Adiciona o diretório raiz do projeto ao sys.path para importações relativas funcionarem
# Este script está na raiz, então 'app' é acessível.
sys.path.append(str(Path(__file__).parent))

from app.run_etl import run_etl_pipeline
from app.query import query_data
from app.config import INPUT_DIR, API_BASE_URL  # Importar API_BASE_URL para mensagens úteis
from app.logger import logger


def main_cli():
    logger.info("Iniciando Agente de IA via CLI.")

    if len(sys.argv) < 2:
        logger.info("Uso: python run.py <comando> [argumentos]")
        logger.info("Comandos disponíveis:")
        logger.info("  etl <arquivo.zip>       - Processa um arquivo ZIP via pipeline ETL.")
        logger.info("  query \"<pergunta>\"    - Faz uma pergunta em linguagem natural ao agente de IA.")
        logger.info("  start_api               - Inicia a API FastAPI (http://0.0.0.0:8000).")
        logger.info("  start_streamlit         - Inicia a interface Streamlit (http://0.0.0.0:8501).")
        return

    command = sys.argv[1].lower()

    if command == "etl":
        if len(sys.argv) < 3:
            logger.error("Uso: python run.py etl <nome_do_arquivo.zip>")
            return
        file_name = sys.argv[2]
        zip_file_path = INPUT_DIR / file_name

        if not zip_file_path.exists():
            logger.error(f"Arquivo não encontrado: {zip_file_path}. Coloque o ZIP em '{INPUT_DIR}'.")
            return

        logger.info(f"Executando ETL para: {file_name}")
        success = run_etl_pipeline(file_name)
        if success:
            logger.info(f"ETL para {file_name} concluído.")
        else:
            logger.error(f"ETL para {file_name} falhou. Verifique os logs para mais detalhes.")

    elif command == "query":
        if len(sys.argv) < 3:
            logger.error("Uso: python run.py query \"Sua pergunta aqui\"")
            return
        question = " ".join(sys.argv[2:])
        logger.info(f"Executando consulta: \"{question}\"")
        result = query_data(question)
        if result.status.startswith("success") or result.status == "warning":
            logger.info("Consulta executada.")
            logger.info(f"Mensagem: {result.message}")
            if result.data is not None and not result.data.empty:  # Verificação melhorada para o DF
                logger.info("\n--- Dados da Consulta ---\n" + result.data.to_string())
            else:
                logger.info("Consulta não retornou dados tabulares explícitos.")
        else:
            logger.error(f"Erro na consulta: {result.message}")

    elif command == "start_api":
        logger.info("Iniciando API FastAPI em http://0.0.0.0:8000...")
        import uvicorn
        from app.api import app as fastapi_app
        uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")

    elif command == "start_streamlit":
        logger.info("Iniciando Streamlit em http://0.0.0.0:8501...")
        # Certifique-se de que o Streamlit é executado a partir da raiz do projeto
        # para que os imports relativos dentro da app funcionem corretamente.
        subprocess.run(
            ["streamlit", "run", "interface/streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"])

    else:
        logger.warning(f"Comando '{command}' não reconhecido.")


if __name__ == "__main__":
    main_cli()