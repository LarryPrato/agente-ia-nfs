# app/extract.py
from pathlib import Path
from collections import namedtuple
import zipfile
import pandas as pd
# Importa TEMP_DIR e logger do diretório 'app' usando importação absoluta
from app.config import TEMP_DIR
from app.logger import logger

# Define um namedtuple para padronizar o resultado da extração
ExtractResult = namedtuple("ExtractResult", ["cabecalho", "itens"])


def extract_zip(file_path: Path) -> ExtractResult:
    """Extrai arquivos CSV de um .zip e retorna como DataFrames."""
    logger.info(f"Iniciando extração do arquivo ZIP: {file_path.name}")
    temp_path = TEMP_DIR # Diretório temporário para extração
    temp_path.mkdir(parents=True, exist_ok=True) # Garante que o diretório exista

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Lista todos os arquivos CSV dentro do ZIP (case-insensitive)
            csv_in_zip = [name for name in zip_ref.namelist() if name.lower().endswith(".csv")]
            logger.info(f"Arquivos CSV encontrados no ZIP: {csv_in_zip}")

            if len(csv_in_zip) < 2:
                raise ValueError("O arquivo ZIP deve conter pelo menos dois arquivos CSV (esperado: cabeçalho e itens).")

            # Extrai todos os arquivos CSV para o diretório temporário
            for csv_name in csv_in_zip:
                zip_ref.extract(csv_name, path=temp_path)
                logger.info(f"Arquivo extraído: {csv_name} para {temp_path}")

        # Após a extração, tenta identificar os arquivos de cabeçalho e itens
        # Busca por "cabecalho" e "itens" (case-insensitive) nos nomes dos arquivos extraídos
        cabecalho_file = next((f for f in temp_path.glob("*.csv") if "cabecalho" in f.name.lower() and f.is_file()), None)
        itens_file = next((f for f in temp_path.glob("*.csv") if "itens" in f.name.lower() and f.is_file()), None)

        if not cabecalho_file:
            logger.warning("Não foi possível identificar o arquivo CSV de 'cabeçalho' pelo nome.")
        if not itens_file:
            logger.warning("Não foi possível identificar o arquivo CSV de 'itens' pelo nome.")

        # Se a identificação pelos nomes falhar, tenta pegar os dois primeiros CSVs
        if not cabecalho_file or not itens_file:
            all_extracted_csvs = sorted([f for f in temp_path.glob("*.csv") if f.is_file()])
            if len(all_extracted_csvs) >= 2:
                # Assume que o primeiro é o cabeçalho e o segundo são os itens
                # Isso é um fallback e pode não ser sempre preciso se os nomes forem genéricos
                if not cabecalho_file: cabecalho_file = all_extracted_csvs[0]
                if not itens_file: itens_file = all_extracted_csvs[1]
                logger.warning(f"Identificação por nome falhou. Assumindo: Cabeçalho='{cabecalho_file.name}', Itens='{itens_file.name}'")
            else:
                raise ValueError(
                    "Não foi possível identificar arquivos CSV de 'cabeçalho' e 'itens' no ZIP. "
                    "Certifique-se de que os nomes contêm 'cabecalho' e 'itens' ou que o ZIP contém exatamente dois CSVs."
                )

        if not cabecalho_file or not itens_file:
            raise ValueError("Não foi possível identificar ambos os arquivos CSV de 'cabeçalho' e 'itens'.")

        logger.info(f"Arquivos CSV identificados: Cabeçalho='{cabecalho_file.name}', Itens='{itens_file.name}'")

        # Tenta ler os arquivos CSV com encoding 'utf-8', fallback para 'latin1'
        try:
            cabecalho_df = pd.read_csv(cabecalho_file, encoding='utf-8', sep=',')
            itens_df = pd.read_csv(itens_file, encoding='utf-8', sep=',')
        except UnicodeDecodeError:
            logger.warning(f"Erro UTF-8 ao ler {file_path.name}. Tentando 'latin1'.")
            cabecalho_df = pd.read_csv(cabecalho_file, encoding='latin1', sep=',')
            itens_df = pd.read_csv(itens_file, encoding='latin1', sep=',')
        except Exception as e:
            logger.error(f"Erro ao ler CSV com ambos os encodings: {e}", exc_info=True)
            raise

        logger.info("Extração e leitura dos DataFrames concluída.")
        return ExtractResult(cabecalho=cabecalho_df, itens=itens_df)

    except FileNotFoundError as e:
        logger.error(f"Arquivo ZIP não encontrado: {e.filename}", exc_info=True)
        raise
    except zipfile.BadZipFile as e:
        logger.error(f"Arquivo ZIP corrompido ou inválido: {e}", exc_info=True)
        raise
    except pd.errors.ParserError as e:
        logger.error(f"Erro ao ler CSV de {file_path.name}: {e}", exc_info=True)
        raise
    except ValueError as e:
        logger.error(f"Erro de extração/identificação em {file_path.name}: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Erro inesperado durante extração de {file_path.name}: {e}", exc_info=True)
        raise
    finally:
        # Limpa os arquivos temporários extraídos
        for file in temp_path.glob("*"):
            if file.is_file():
                try:
                    file.unlink() # Remove o arquivo
                    logger.debug(f"Arquivo temporário removido: {file.name}")
                except OSError as e:
                    logger.warning(f"Não foi possível remover arquivo temporário '{file.name}': {e}")
        logger.info(f"Arquivos temporários em {temp_path} limpos.")