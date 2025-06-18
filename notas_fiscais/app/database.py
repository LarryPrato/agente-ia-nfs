import sqlite3
import pandas as pd
from collections import namedtuple
# Importa DB_PATH e logger do diretório 'app' usando importação absoluta
from app.config import DB_PATH
from app.logger import logger

# Define um namedtuple para padronizar os resultados das operações de banco de dados
DatabaseResult = namedtuple("DatabaseResult", ["status", "message"])


def save_to_database(df: pd.DataFrame) -> DatabaseResult:
    """Salva o DataFrame combinado no banco de dados SQLite, criando/substituindo a tabela dinamicamente."""
    logger.info(f"Salvando dados em {DB_PATH}")
    if df.empty:
        msg = "DataFrame vazio, nada para salvar."
        logger.warning(msg)
        return DatabaseResult(status="warning", message=msg)

    conn = None # Inicializa a conexão como None
    try:
        # Conecta ao banco de dados SQLite. Se o arquivo não existir, ele será criado.
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        table_name = "notas_fiscais" # Nome da tabela no banco de dados

        # Gera as definições de coluna para a instrução CREATE TABLE
        column_definitions = []
        df_columns = df.columns.tolist()

        pk_column = None
        # Procura por uma coluna candidata a chave primária
        # Preferência para chaves que identifiquem unicamente as notas fiscais
        for key_candidate in ["chave_de_acesso", "chave", "id_nota", "numero_nf", "id"]:
            if key_candidate in df_columns:
                pk_column = key_candidate
                break

        if pk_column:
            # Adiciona a chave primária com tipo TEXT
            column_definitions.append(f"{pk_column} TEXT PRIMARY KEY")
            df_columns.remove(pk_column)  # Remove da lista para evitar duplicidade
        else:
            logger.warning("Nenhuma coluna candidata a PRIMARY KEY encontrada. A tabela pode ter chaves duplicadas.")
            # Se não há PK, pode-se adicionar uma PK AUTOINCREMENT, mas para simplicidade, deixamos assim.

        # Itera sobre as colunas restantes para inferir o tipo SQL
        for col in df_columns:
            # Normaliza o nome da coluna para ser seguro para SQL
            safe_col_name = "".join(c if c.isalnum() else "_" for c in col)

            if pd.api.types.is_integer_dtype(df[col]):
                sql_type = "INTEGER"
            elif pd.api.types.is_float_dtype(df[col]):
                sql_type = "REAL"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                sql_type = "TEXT" # Armazena datas como TEXT (formato ISO)
                df[col] = df[col].astype(str)  # Converte para string ISO formatada
            elif pd.api.types.is_bool_dtype(df[col]):
                sql_type = "INTEGER"  # SQLite não tem BOOLEAN nativo, usa INTEGER (0 ou 1)
                df[col] = df[col].astype(int)
            else:  # Fallback para TEXT para strings e outros tipos
                sql_type = "TEXT"
                # Se houver listas/dicts, serializá-los para string
                if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                    df[col] = df[col].astype(str)

            # Adiciona a definição da coluna (nome_seguro TIPO_SQL)
            column_definitions.append(f"{safe_col_name} {sql_type}")

        # Cria a instrução SQL para criar a tabela.
        # Usa um set para garantir colunas únicas, caso haja alguma duplicação acidental
        # e então junta com vírgula.
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(set(column_definitions))})"

        logger.info(f"Criando/atualizando esquema da tabela '{table_name}'. SQL: {create_table_sql}")
        cursor.execute(create_table_sql) # Executa a criação da tabela
        conn.commit() # Confirma a transação

        # Usa df.to_sql para inserir os dados.
        # if_exists='replace' sobrescreve a tabela inteira se ela já existe.
        # index=False evita que o índice do DataFrame seja salvo como uma coluna.
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.commit() # Confirma a transação de inserção

        logger.info(f"Dados salvos em '{table_name}'. Total de registros: {len(df)}")
        return DatabaseResult(status="success", message="Dados salvos com sucesso.")

    except sqlite3.Error as e:
        logger.error(f"Erro SQLite: {e}", exc_info=True)
        if conn:
            conn.rollback() # Reverte a transação em caso de erro
        return DatabaseResult(status="error", message=f"Erro no banco de dados: {str(e)}")
    except Exception as e:
        logger.error(f"Erro inesperado ao salvar: {e}", exc_info=True)
        if conn:
            conn.rollback() # Reverte a transação em caso de erro
        return DatabaseResult(status="error", message=f"Erro inesperado ao salvar: {str(e)}")
    finally:
        if conn:
            conn.close() # Sempre fecha a conexão
            logger.info("Conexão DB fechada.")