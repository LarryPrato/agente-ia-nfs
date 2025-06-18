from pathlib import Path
from extract import extract_zip
from transform import combine_data
from database import save_to_database
from logger import logger
from config import INPUT_DIR

def run_etl_pipeline(file_name: str) -> bool:
    """Executa o pipeline completo de ETL para um arquivo ZIP."""
    file_path = INPUT_DIR / file_name
    logger.info(f"Iniciando ETL para: {file_path.name}")

    try:
        extract_result = extract_zip(file_path)
        if extract_result.cabecalho.empty and extract_result.itens.empty: # Ambos vazios é um problema
            logger.error(f"Extração de {file_path.name} resultou em DataFrames vazios.")
            return False
    except Exception as e:
        logger.error(f"Falha na etapa de extração para {file_path.name}: {e}", exc_info=True)
        return False

    try:
        transform_result = combine_data(extract_result.cabecalho, extract_result.itens)
        if not transform_result.status.startswith("success") or transform_result.combined_df.empty:
            logger.error(f"Falha na etapa de transformação para {file_path.name}: {transform_result.message}")
            return False
    except Exception as e:
        logger.error(f"Falha na etapa de transformação para {file_path.name}: {e}", exc_info=True)
        return False

    try:
        database_result = save_to_database(transform_result.combined_df)
        if not database_result.status.startswith("success"):
            logger.error(f"Falha ao salvar dados de {file_path.name} no DB: {database_result.message}")
            return False
        logger.info(f"ETL para {file_name} concluído com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Falha ao salvar dados de {file_path.name} no DB: {e}", exc_info=True)
        return False