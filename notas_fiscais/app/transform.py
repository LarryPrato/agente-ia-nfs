from collections import namedtuple
import pandas as pd
# Importa o logger do diretório 'app' usando importação absoluta
from app.logger import logger

# Define um namedtuple para padronizar o resultado da transformação
TransformResult = namedtuple("TransformResult", ["combined_df", "status", "message"])


def combine_data(cabecalho_df: pd.DataFrame, itens_df: pd.DataFrame) -> TransformResult:
    """
    Combina os DataFrames de cabeçalho e itens em um único DataFrame,
    realizando normalização de colunas e tratamento de tipos.
    """
    logger.info("Iniciando combinação e transformação dos DataFrames.")

    # Verifica se algum dos DataFrames de entrada está vazio
    if cabecalho_df.empty or itens_df.empty:
        msg = "Um ou ambos os DataFrames (cabeçalho/itens) estão vazios. Não é possível combinar."
        logger.warning(msg)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)

    def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza os nomes das colunas de um DataFrame para um formato SQL-friendly."""
        original_columns = df.columns.tolist()
        df.columns = [
            col.strip().lower()  # Remove espaços e converte para minúsculas
            .replace(' ', '_').replace('-', '_').replace('ç', 'c').replace('ã', 'a')
            .replace('õ', 'o').replace('ú', 'u').replace('é', 'e').replace('á', 'a')
            .replace('.', '').replace('/', '_')  # Remove caracteres especiais e substitui por underscore
            for col in df.columns
        ]
        logger.info(f"Colunas normalizadas. Original: {original_columns}, Nova: {df.columns.tolist()}")
        return df

    # Normaliza as colunas de ambos os DataFrames
    cabecalho_df = normalize_columns(cabecalho_df.copy())  # Usar .copy() para evitar SettingWithCopyWarning
    itens_df = normalize_columns(itens_df.copy())

    # Busca por chaves de junção potenciais em ordem de preferência
    possible_keys = ["chave_de_acesso", "chave", "numero_nf", "id_nota", "id"]
    join_key = None
    for pk in possible_keys:
        if pk in cabecalho_df.columns and pk in itens_df.columns:
            join_key = pk
            logger.info(f"Chave de junção identificada: '{join_key}'")
            break

    if not join_key:
        msg = f"Nenhuma chave de junção comum encontrada entre os DataFrames. Esperado uma das: {possible_keys}"
        logger.error(msg)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)

    try:
        # Converter a chave de junção para string e remover espaços em branco para garantir a compatibilidade na junção
        cabecalho_df[join_key] = cabecalho_df[join_key].astype(str).str.strip()
        itens_df[join_key] = itens_df[join_key].astype(str).str.strip()

        # Normalização de colunas numéricas: converte para numérico e preenche NaNs com 0
        numeric_cols_cab = [col for col in ['valor_total', 'valor_total_da_nota', 'valor_total_nota'] if
                            col in cabecalho_df.columns]
        numeric_cols_item = [col for col in ['valor_do_item', 'quantidade', 'preco_unitario', 'valor_unitario'] if
                             col in itens_df.columns]

        for col in numeric_cols_cab:
            cabecalho_df[col] = pd.to_numeric(cabecalho_df[col], errors='coerce').fillna(0)
            logger.debug(f"Coluna numérica cabeçalho processada: {col}")
        for col in numeric_cols_item:
            itens_df[col] = pd.to_numeric(itens_df[col], errors='coerce').fillna(0)
            logger.debug(f"Coluna numérica item processada: {col}")

        # Preencher NaNs em colunas de objeto (strings) com string vazia para evitar erros de tipo na junção ou no DB
        for col in cabecalho_df.select_dtypes(include=['object']).columns:
            cabecalho_df[col] = cabecalho_df[col].fillna('')
        for col in itens_df.select_dtypes(include=['object']).columns:
            itens_df[col] = itens_df[col].fillna('')

    except Exception as e:
        msg = f"Erro na normalização de tipos/chave ou preenchimento de NaNs: {e}"
        logger.error(msg, exc_info=True)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)

    try:
        # Realiza a junção (merge) dos DataFrames usando a chave identificada
        # how="left" garante que todas as notas do cabeçalho sejam mantidas
        # suffixes adiciona sufixos para colunas com nomes duplicados (e.g., id_cab, id_item)
        combined_df = pd.merge(cabecalho_df, itens_df, on=join_key, how="left", suffixes=('_cab', '_item'))

        # Adiciona uma coluna 'processed_at' com a data e hora do processamento
        combined_df["processed_at"] = pd.Timestamp.now().isoformat()

        logger.info(f"Transformação concluída. DataFrame combinado possui shape: {combined_df.shape}")
        return TransformResult(combined_df=combined_df, status="success", message="Dados combinados com sucesso.")

    except KeyError as e:
        msg = f"Erro de chave durante a junção: {e}. Colunas essenciais para o merge ausentes."
        logger.error(msg, exc_info=True)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)
    except Exception as e:
        msg = f"Erro inesperado durante a combinação dos DataFrames: {e}"
        logger.error(msg, exc_info=True)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)