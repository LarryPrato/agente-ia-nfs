from collections import namedtuple
import pandas as pd
from logger import logger

TransformResult = namedtuple("TransformResult", ["combined_df", "status", "message"])


def combine_data(cabecalho_df: pd.DataFrame, itens_df: pd.DataFrame) -> TransformResult:
    """Combina os DataFrames de cabeçalho e itens em um único DataFrame, com normalização."""
    logger.info("Iniciando combinação e transformação.")

    if cabecalho_df.empty or itens_df.empty:
        msg = "Um ou ambos os DataFrames (cabeçalho/itens) estão vazios."
        logger.warning(msg)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)

    def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = [
            col.strip().lower()
            .replace(' ', '_').replace('-', '_').replace('ç', 'c').replace('ã', 'a')
            .replace('õ', 'o').replace('ú', 'u').replace('é', 'e').replace('á', 'a')
            .replace('.', '').replace('/', '_')
            for col in df.columns
        ]
        return df

    cabecalho_df = normalize_columns(cabecalho_df)
    itens_df = normalize_columns(itens_df)

    # Buscar chaves de junção potenciais em ordem de preferência
    possible_keys = ["chave_de_acesso", "chave", "numero_nf", "id_nota", "id"]  # Adicionado "id"
    join_key = None
    for pk in possible_keys:
        if pk in cabecalho_df.columns and pk in itens_df.columns:
            join_key = pk
            break

    if not join_key:
        msg = f"Nenhuma chave de junção comum encontrada. Esperado uma das: {possible_keys}"
        logger.error(msg)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)

    try:
        # Converter a chave de junção para string para garantir compatibilidade
        cabecalho_df[join_key] = cabecalho_df[join_key].astype(str).str.strip()
        itens_df[join_key] = itens_df[join_key].astype(str).str.strip()

        # Normalização de colunas numéricas
        numeric_cols_cab = [col for col in ['valor_total', 'valor_total_da_nota', 'valor_total_nota'] if
                            col in cabecalho_df.columns]
        numeric_cols_item = [col for col in ['valor_do_item', 'quantidade', 'preco_unitario', 'valor_unitario'] if
                             col in itens_df.columns]

        for col in numeric_cols_cab:
            cabecalho_df[col] = pd.to_numeric(cabecalho_df[col], errors='coerce').fillna(0)
        for col in numeric_cols_item:
            itens_df[col] = pd.to_numeric(itens_df[col], errors='coerce').fillna(0)

        # Preencher NaNs em colunas de objeto com string vazia para evitar erros de tipo na junção
        for col in cabecalho_df.select_dtypes(include=['object']).columns:
            cabecalho_df[col] = cabecalho_df[col].fillna('')
        for col in itens_df.select_dtypes(include=['object']).columns:
            itens_df[col] = itens_df[col].fillna('')

    except Exception as e:
        msg = f"Erro na normalização de tipos/chave: {e}"
        logger.error(msg, exc_info=True)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)

    try:
        combined_df = pd.merge(cabecalho_df, itens_df, on=join_key, how="left", suffixes=('_cab', '_item'))
        combined_df["processed_at"] = pd.Timestamp.now().isoformat()

        logger.info(f"Transformação concluída. Shape: {combined_df.shape}")
        return TransformResult(combined_df=combined_df, status="success", message="Dados combinados com sucesso.")

    except KeyError as e:
        msg = f"Erro de chave durante junção: {e}. Colunas essenciais ausentes."
        logger.error(msg, exc_info=True)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)
    except Exception as e:
        msg = f"Erro inesperado durante a combinação: {e}"
        logger.error(msg, exc_info=True)
        return TransformResult(combined_df=pd.DataFrame(), status="error", message=msg)