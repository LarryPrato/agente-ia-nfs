.PHONY: build run run-local stop clean test download-model help

# Variáveis
APP_NAME := ai_agents_v3_optimized
API_PORT := 8000
STREAMLIT_PORT := 8501
LOCAL_MODEL_NAME := mistral-7b-instruct-v0.2.Q4_K_M.gguf
# URL para download do modelo Mistral 7B Instruct v0.2 Q4_K_M GGUF
MODEL_DOWNLOAD_URL := https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf?download=true

# Constrói as imagens Docker
build:
	@echo "Construindo imagens Docker para $(APP_NAME)..."
	docker-compose build

# Inicia a aplicação em modo cloud (padrão, com base no .env ou docker-compose.yml)
run: build
	@echo "Iniciando aplicação em modo Cloud-First (usando .env ou padrão docker-compose)..."
	docker-compose up --build -d
	@echo "Aplicação rodando:"
	@echo "  API: http://localhost:$(API_PORT)"
	@echo "  Streamlit: http://localhost:$(STREAMLIT_PORT)"
	@echo "Verifique os logs com 'docker-compose logs -f'"

# Inicia a aplicação em modo local (força ENV=local)
run-local: build
	@echo "Iniciando aplicação em modo Local-Friendly (forçando ENV=local)..."
	@echo "Certifique-se de ter o modelo GGUF baixado em ./models/$(LOCAL_MODEL_NAME) (use 'make download-model')"
	# Para carregar o .env e sobrescrever ENV para 'local'
	@echo "ENV=local" > .env.temp # Cria um arquivo .env temporário
	cat .env >> .env.temp # Adiciona o conteúdo do .env original
	docker-compose --env-file .env.temp up --build -d
	rm .env.temp # Remove o arquivo temporário
	@echo "Aplicação rodando:"
	@echo "  API: http://localhost:$(API_PORT)"
	@echo "  Streamlit: http://localhost:$(STREAMLIT_PORT)"
	@echo "Verifique os logs com 'docker-compose logs -f'"


# Para os serviços Docker
stop:
	@echo "Parando os serviços Docker..."
	docker-compose down

# Limpa o ambiente (remove volumes, imagens, dados e modelos)
clean: stop
	@echo "Limpando o ambiente (parando serviços, removendo volumes, imagens, dados e modelos)..."
	docker-compose down --rmi all -v
	rm -rf data/*
	rm -rf models/*
	@echo "Ambiente limpo."

# Executa os testes dentro do container da API
test: build
	@echo "Executando testes..."
	docker-compose run --rm api pytest tests/
	@echo "Testes concluídos."

# Baixa o modelo GGUF (Mistral) para uso local
download-model:
	@echo "Criando diretório 'models/' se não existir..."
	mkdir -p models
	@echo "Baixando o modelo GGUF para ./models/$(LOCAL_MODEL_NAME)... Isso pode levar algum tempo e o tamanho é de ~4GB."
	@curl -L "$(MODEL_DOWNLOAD_URL)" -o models/$(LOCAL_MODEL_NAME)
	@echo "Download do modelo concluído."

help:
	@echo "--------------------------------------------------------"
	@echo "         Ajuda - Projeto AI Agents para Notas Fiscais"
	@echo "--------------------------------------------------------"
	@echo "Comandos disponíveis:"
	@echo "  make build          - Constrói as imagens Docker."
	@echo "  make run            - Inicia a aplicação em modo Cloud-First (padrão)."
	@echo "                      (Usa o LLM configurado em .env ou como padrão no docker-compose.yml)"
	@echo "  make run-local      - Inicia a aplicação em modo Local-Friendly (força ENV=local)."
	@echo "                      (Requer 'make download-model' antes, para usar LLM GGUF localmente)"
	@echo "  make stop           - Para todos os serviços Docker da aplicação."
	@echo "  make clean          - Para serviços, remove imagens, volumes e limpa pastas de dados/modelos."
	@echo "  make test           - Executa os testes automatizados da aplicação."
	@echo "  make download-model - Baixa o modelo LLM GGUF para uso offline (Mistral-7B-Instruct-v0.2)."
	@echo "  make help           - Mostra esta mensagem de ajuda."
	@echo "--------------------------------------------------------"