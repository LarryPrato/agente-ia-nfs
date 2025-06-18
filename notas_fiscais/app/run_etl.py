# Importa as funções das etapas do pipeline, usando importações absolutas dentro do pacote 'app'
from app.extract import extract_zip
from app.transform import combine_data
from app.database import save_to_database
# Importa o logger e o diretório de entrada
from app.logger import logger
from app.config import INPUT_DIR

def run_etl_pipeline(file_name: str) -> bool:
    """
    Executa o pipeline completo de ETL (Extract, Transform, Load) para um arquivo ZIP.

    Args:
        file_name (str): O nome do arquivo ZIP a ser processado, localizado em INPUT_DIR.

    Returns:
        bool: True se o pipeline for concluído com sucesso, False caso contrário.
    """
    file_path = INPUT_DIR / file_name
    logger.info(f"Iniciando pipeline ETL para o arquivo: {file_path.name}")

    # ETAPA 1: EXTRAÇÃO
    try:
        logger.info(f"Iniciando etapa de extração para {file_path.name}")
        extract_result = extract_zip(file_path) # Extrai os CSVs do ZIP para DataFrames
        # Verifica se os DataFrames resultantes da extração estão vazios
        if extract_result.cabecalho.empty or extract_result.itens.empty:
            logger.error(f"Extração de {file_path.name} resultou em DataFrames vazios ou incompletos.")
            return False # Falha na extração
        logger.info(f"Etapa de extração concluída com sucesso para {file_path.name}. "
                    f"Cabeçalho shape: {extract_result.cabecalho.shape}, Itens shape: {extract_result.itens.shape}")
    except Exception as e:
        logger.error(f"Falha crítica na etapa de extração para {file_path.name}: {e}", exc_info=True)
        return False # Falha na extração

    # ETAPA 2: TRANSFORMAÇÃO
    try:
        logger.info(f"Iniciando etapa de transformação para {file_path.name}")
        # Combina os DataFrames de cabeçalho e itens
        transform_result = combine_data(extract_result.cabecalho, extract_result.itens)
        # Verifica o status e se o DataFrame combinado não está vazio
        if not transform_result.status.startswith("success") or transform_result.combined_df.empty:
            logger.error(f"Falha na etapa de transformação para {file_path.name}: {transform_result.message}")
            return False # Falha na transformação
    except Exception as e:
        logger.error(f"Falha crítica na etapa de transformação para {file_path.name}: {e}", exc_info=True)
        return False # Falha na transformação

    # ETAPA 3: CARREGAMENTO (LOAD)
    try:
        logger.info(f"Iniciando etapa de carregamento (load) para {file_path.name}")
        # Salva o DataFrame combinado no banco de dados
        database_result = save_to_database(transform_result.combined_df)
        # Verifica o status do salvamento no banco de dados
        if not database_result.status.startswith("success"):
            logger.error(f"Falha ao salvar dados de {file_path.name} no banco de dados: {database_result.message}")
            return False # Falha no carregamento
        logger.info(f"Etapa de carregamento (load) concluída com sucesso para {file_path.name}.")
        logger.info(f"Pipeline ETL para {file_name} concluído com sucesso.")
        return True # Pipeline ETL concluído com sucesso
    except Exception as e:
        logger.error(f"Falha crítica na etapa de carregamento (load) para {file_path.name}: {e}", exc_info=True)
        return False # Falha no carregamento