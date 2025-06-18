from pathlib import Path
from collections import namedtuple
import zipfile
import pandas as pd
from config import TEMP_DIR
from logger import logger

ExtractResult = namedtuple("ExtractResult", ["cabecalho", "itens"])


def extract_zip(file_path: Path) -> ExtractResult:
    """Extrai arquivos CSV de um .zip e retorna como DataFrames."""
    logger.info(f"Extraindo: {file_path.name}")
    temp_path = TEMP_DIR
    temp_path.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            csv_in_zip = [name for name in zip_ref.namelist() if name.lower().endswith(".csv")]
            if len(csv_in_zip) < 2:
                raise ValueError("O arquivo ZIP deve conter pelo menos dois arquivos CSV (cabeçalho e itens).")

            for csv_name in csv_in_zip:
                zip_ref.extract(csv_name, path=temp_path)

        # Usar glob mais específico e verificar se os arquivos existem após extração
        cabecalho_file = next((f for f in temp_path.glob("*cabecalho*.csv") if f.is_file()), None)
        itens_file = next((f for f in temp_path.glob("*itens*.csv") if f.is_file()), None)

        if not cabecalho_file or not itens_file:
            # Caso os nomes não contenham "cabecalho" ou "itens" mas sejam os únicos CSVs
            if len(csv_in_zip) == 2:
                csv_files_extracted = sorted([f for f in temp_path.glob("*.csv") if f.is_file()])
                if len(csv_files_extracted) == 2:
                    cabecalho_file = csv_files_extracted[0]  # Assumir o primeiro
                    itens_file = csv_files_extracted[1]  # Assumir o segundo
                else:
                    raise ValueError(
                        "Não foi possível identificar arquivos CSV de 'cabeçalho' e 'itens' no ZIP. Certifique-se de que os nomes contêm 'cabecalho' e 'itens' ou que são apenas dois CSVs.")
            else:
                raise ValueError(
                    "Não foi possível identificar arquivos CSV de 'cabeçalho' e 'itens' no ZIP. Certifique-se de que os nomes contêm 'cabecalho' e 'itens' ou que são apenas dois CSVs.")

        try:
            cabecalho_df = pd.read_csv(cabecalho_file, encoding='utf-8')
            itens_df = pd.read_csv(itens_file, encoding='utf-8')
        except UnicodeDecodeError:
            logger.warning(f"Erro UTF-8 em {file_path.name}. Tentando 'latin1'.")
            cabecalho_df = pd.read_csv(cabecalho_file, encoding='latin1')
            itens_df = pd.read_csv(itens_file, encoding='latin1')

        logger.info("Extração concluída.")
        return ExtractResult(cabecalho=cabecalho_df, itens=itens_df)

    except FileNotFoundError as e:
        logger.error(f"Arquivo ZIP não encontrado: {e.filename}", exc_info=True)
        raise
    except zipfile.BadZipFile as e:
        logger.error(f"ZIP corrompido ou inválido: {e}", exc_info=True)
        raise
    except pd.errors.ParserError as e:
        logger.error(f"Erro ao ler CSV de {file_path.name}: {e}", exc_info=True)
        raise
    except ValueError as e:
        logger.error(f"Erro de extração em {file_path.name}: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Erro inesperado durante extração de {file_path.name}: {e}", exc_info=True)
        raise
    finally:
        for file in temp_path.glob("*"):
            if file.is_file():
                try:
                    file.unlink()
                except OSError as e:
                    logger.warning(f"Não foi possível remover temp file {file.name}: {e}")
        logger.info(f"Arquivos temporários em {temp_path} limpos.")