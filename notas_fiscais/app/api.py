from fastapi import FastAPI, UploadFile, File, HTTPException, status
from app.query import query_data, QueryResult
from app.run_etl import run_etl_pipeline
from app.config import INPUT_DIR, TEMP_DIR  # Importar TEMP_DIR para limpeza
from app.logger import logger
import os

app = FastAPI(
    title="API de Notas Fiscais com Agentes de IA",
    version="1.0.0",
    description="API para upload de dados de notas fiscais (ZIP) e consulta em linguagem natural usando agentes de IA.",
)

@app.post("/upload-and-process/", status_code=status.HTTP_200_OK)
async def upload_and_process_file(file: UploadFile = File(...)):
    """Faz upload de um arquivo .zip e o processa via pipeline ETL."""
    logger.info(f"Upload recebido: {file.filename}")

    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apenas arquivos .zip são permitidos.")

    # Salva o arquivo temporariamente em INPUT_DIR para que run_etl_pipeline possa acessá-lo
    file_path = INPUT_DIR / file.filename
    try:
        # Abre o arquivo em modo de escrita binária e escreve o conteúdo do upload
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"Arquivo '{file.filename}' salvo temporariamente em '{file_path}'.")

        # Executa o pipeline ETL com o nome do arquivo ZIP
        success = run_etl_pipeline(file.filename)

        if success:
            logger.info(f"Processamento de {file.filename} concluído.")
            return {"status": "success", "message": f"Arquivo '{file.filename}' processado e dados salvos com sucesso."}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Falha no processamento de '{file.filename}'. Verifique os logs da API."
            )
    except Exception as e:
        logger.error(f"Erro ao processar {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Erro interno no servidor: {str(e)}")
    finally:
        # Garante a limpeza do arquivo ZIP temporário após o processamento
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Arquivo temporário '{file.filename}' removido.")
            except OSError as e:
                logger.warning(f"Não foi possível remover arquivo temporário '{file.filename}': {e}")
        # Limpar também o diretório TEMP_DIR, que é usado pela extração
        for temp_file in TEMP_DIR.glob("*"):
            if temp_file.is_file():
                try:
                    temp_file.unlink()
                except OSError as e:
                    logger.warning(f"Não foi possível remover arquivo temp de extração '{temp_file.name}': {e}")


@app.get("/query/", status_code=status.HTTP_200_OK)
def query(question: str):
    """Endpoint para enviar uma pergunta em linguagem natural ao agente de IA."""
    logger.info(f"Consulta API recebida: '{question}'")

    result: QueryResult = query_data(question)

    if result.status.startswith("success") or result.status == "warning":
        # Converter DataFrame para lista de dicionários para JSON response
        response_data = result.data.to_dict(orient="records") if not result.data.empty else None
        return {
            "data": response_data,
            "status": result.status,
            "message": result.message
        }
    else:
        # Se o status for "error", retorna um erro HTTP 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result.message)