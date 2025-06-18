# Use uma imagem base Python slim para menor tamanho e compatibilidade com llama-cpp-python
FROM python:3.10-slim-buster

# Instala dependências de sistema para llama-cpp-python (build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependência e instala
COPY requirements.txt .
# Instala com --no-cache-dir para economizar espaço e --prefer-binary para otimização
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copia o restante da aplicação
COPY . .

# Cria os diretórios necessários no build para garantir que existam
RUN mkdir -p data/input data/temp data/logs models

# Expõe as portas para a API FastAPI e Streamlit
EXPOSE 8000
EXPOSE 8501

# Comando padrão para iniciar a API FastAPI
# Pode ser sobrescrito pelo docker-compose ou makefile
CMD ["python", "run.py", "start_api"]