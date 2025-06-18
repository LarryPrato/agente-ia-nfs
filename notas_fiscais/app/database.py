import sqlite3
import pandas as pd
from collections import namedtuple
from config import DB_PATH
from logger import logger

DatabaseResult = namedtuple("DatabaseResult", ["status", "message"])


def save_to_database(df: pd.DataFrame) -> DatabaseResult:
    """Salva o DataFrame combinado no banco de dados SQLite, criando a tabela dinamicamente."""
    logger.info(f"Salvando dados em {DB_PATH}")
    if df.empty:
        msg = "DataFrame vazio, nada para salvar."
        logger.warning(msg)
        return DatabaseResult(status="warning", message=msg)

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        table_name = "notas_fiscais"

        column_definitions = []
        df_columns = df.columns.tolist()

        pk_column = None
        # Procurar uma coluna que possa ser chave primária
        for key_candidate in ["chave_de_acesso", "chave", "id_nota", "numero_nf", "id"]:
            if key_candidate in df_columns:
                pk_column = key_candidate
                break

        if pk_column:
            column_definitions.append(f"{pk_column} TEXT PRIMARY KEY")
            df_columns.remove(pk_column)  # Remover da lista para não adicionar duas vezes
        else:
            logger.warning("Nenhuma coluna candidata a PRIMARY KEY encontrada. A tabela pode ter chaves duplicadas.")

        for col in df_columns:
            # Substituir caracteres inválidos em nomes de coluna para SQL
            safe_col_name = "".join(c if c.isalnum() else "_" for c in col)

            if pd.api.types.is_integer_dtype(df[col]):
                sql_type = "INTEGER"
            elif pd.api.types.is_float_dtype(df[col]):
                sql_type = "REAL"
            # Verificar se é datetime antes de object, pois datetime pode ser object
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                sql_type = "TEXT"
                df[col] = df[col].astype(str)  # Converter para string ISO formatada
            elif pd.api.types.is_bool_dtype(df[col]):
                sql_type = "INTEGER"  # SQLite não tem BOOLEAN nativo, usa INTEGER (0 ou 1)
                df[col] = df[col].astype(int)
            else:  # Fallback para TEXT para strings, listas, dicts, etc.
                sql_type = "TEXT"
                # Se houver listas/dicts, serializá-los para string
                if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                    df[col] = df[col].astype(str)

            column_definitions.append(f"{safe_col_name} {sql_type}")

        # Se houver uma chave primária, garantir que ela está na ordem correta
        final_columns_for_create = []
        if pk_column:
            final_columns_for_create.append(f"{pk_column} TEXT PRIMARY KEY")

        for col_def in column_definitions:
            # Adicionar apenas colunas que não são a PK já adicionada
            if pk_column and col_def.startswith(f"{pk_column} "):
                continue
            final_columns_for_create.append(col_def)

        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(final_columns_for_create)})"

        logger.info(f"Criando/atualizando esquema da tabela '{table_name}'.")
        cursor.execute(create_table_sql)
        conn.commit()

        # Usar df.to_sql com if_exists='append' se quiser adicionar, ou 'replace' para substituir
        # Para evitar duplicatas na PK, 'replace' é mais simples aqui.
        # Se a intenção for atualizar apenas novas notas ou as existentes, uma estratégia de UPSERT seria necessária.
        # Por simplicidade, `replace` sobrescreve a tabela.
        df.to_sql(table_name, conn, if_exists="replace",
                  index=False)  # 'append' para adicionar, 'replace' para sobrescrever
        conn.commit()

        logger.info(f"Dados salvos em '{table_name}'. Total de registros: {len(df)}")
        return DatabaseResult(status="success", message="Dados salvos com sucesso.")

    except sqlite3.Error as e:
        logger.error(f"Erro SQLite: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return DatabaseResult(status="error", message=f"Erro no banco de dados: {str(e)}")
    except Exception as e:
        logger.error(f"Erro inesperado ao salvar: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return DatabaseResult(status="error", message=f"Erro inesperado ao salvar: {str(e)}")
    finally:
        if conn:
            conn.close()
            logger.info("Conexão DB fechada.")