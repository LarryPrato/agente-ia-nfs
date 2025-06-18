import logging
from logging.handlers import RotatingFileHandler
from config import LOGS_DIR


def setup_logging():
    log_file = LOGS_DIR / "app.log"

    # Criar logger principal
    logger = logging.getLogger("ai_agents_logger")  # Nomear o logger para evitar conflitos
    logger.setLevel(logging.INFO)  # Nível padrão INFO para produção

    # Evitar adicionar múltiplos handlers se já existirem
    if not logger.handlers:
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Console também em INFO
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Handler para arquivo, com rotação
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024,
                                           backupCount=5)  # 5 MB por arquivo, 5 arquivos
        file_handler.setLevel(logging.INFO)  # Arquivo também em INFO
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Configurar loggers de bibliotecas externas para evitar verbosidade excessiva
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('langchain').setLevel(logging.WARNING)  # Manter LangChain WARNING por padrão
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)  # Evita logs de SQLAlchemy
    logging.getLogger('urllib3').setLevel(logging.WARNING)  # Evita logs de requisições
    # uvicorn e fastapi são loggers próprios, e o uvicorn.run já tem seu controle de log_level

    return logger


# Inicializa o logger ao importar
logger = setup_logging()