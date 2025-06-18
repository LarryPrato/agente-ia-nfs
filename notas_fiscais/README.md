# AI Agents para Análise de Notas Fiscais

Este projeto implementa um sistema de ETL (Extract, Transform, Load) e um agente de IA para consultar dados de notas fiscais em linguagem natural. Ele suporta tanto modelos de LLM em nuvem (HuggingFace) quanto modelos locais (GGUF via LlamaCpp).

## 🚀 Funcionalidades

* **ETL Automatizado**: Extrai dados de arquivos ZIP (cabeçalho e itens), transforma-os e os carrega em um banco de dados SQLite.
* **Agente de IA**: Permite consultas em linguagem natural sobre os dados das notas fiscais, utilizando um LLM e LangChain SQL Agent.
* **Ambiente Híbrido**: Suporte para LLMs em nuvem (ex: Flan-T5, Mistral) e LLMs locais (modelos GGUF).
* **Interface Web**: Aplicação Streamlit para upload de arquivos e interação com o agente de IA.
* **API REST**: Endpoint FastAPI para integração programática.

## 📦 Estrutura do Projeto

notas_fiscais/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── README.md
├── requirements.txt
├── setup.py
├── run.py
│
├── app/
│   ├── init.py
│   ├── config.py
│   ├── logger.py
│   ├── extract.py
│   ├── transform.py
│   ├── database.py
│   ├── query.py
│   ├── run_etl.py
│   └── api.py
│
├── interface/
│   └── streamlit_app.py
│
├── models/
│   └── .gitkeep
│
├── data/
│   ├── input/
│   ├── temp/
│   ├── logs/
│   └── notas.db
│
└── tests/
├── init.py
├── conftest.py
├── test_extract.py
├── test_transform.py
├── test_database.py
└── test_query.py

## ⚙️ Configuração e Instalação

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/ai_agents_notas_fiscais.git](https://github.com/seu-usuario/ai_agents_notas_fiscais.git)
    cd ai_agents_notas_fiscais
    ```

2.  **Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz do projeto, copiando e configurando o `.env.example`:
    ```bash
    cp .env.example .env
    # Edite .env com suas preferências (ENV=local/cloud, LLM_CLOUD_MODEL_NAME, LLM_LOCAL_MODEL_PATH, etc.)
    ```

3.  **Configuração Inicial (Host ou Docker):**

    * **Opção A: Rodar Diretamente no Host (Recomendado para Desenvolvimento):**
        ```bash
        python -m venv venv
        source venv/bin/activate # ou `.\venv\Scripts\activate` no Windows
        pip install -r requirements.txt
        python setup.py # Cria diretórios, etc.
        # Se ENV=local, você precisará baixar o modelo GGUF manualmente ou usar `make download-model`
        ```

    * **Opção B: Rodar com Docker (Recomendado para Produção/Implantação):**
        Certifique-se de ter Docker e Docker Compose instalados.
        ```bash
        docker-compose up --build -d
        ```

4.  **Baixar Modelo Local (se `ENV=local` no `.env`):**
    ```bash
    make download-model
    ```
    (Este comando usará a URL padrão ou a configurada no `Makefile` para baixar o modelo GGUF para `models/`).

## 🚀 Como Usar

### 1. Via Interface Web (Streamlit)

Após iniciar com Docker Compose (`docker-compose up -d`) ou localmente:
bash
# Se localmente
`streamlit run interface/streamlit_app.py`

Acesse http://localhost:8501 no seu navegador.

Upload: Use a seção "Upload e Processamento de Dados" para enviar um arquivo ZIP.
Consulta: Use a seção "Consulte Seus Dados" para fazer perguntas em linguagem natural.

### 2. Via API (FastAPI)
Após iniciar com Docker Compose (docker-compose up -d) ou localmente:

# Se localmente
`python run.py start_api`

Acesse http://localhost:8000/docs para a documentação interativa da API (Swagger UI).

/upload-and-process/ (POST): Para enviar arquivos ZIP.
/query/ (GET): Para enviar perguntas.


### 3. Via Linha de Comando (CLI)
Use o script run.py para interagir diretamente com o sistema.

Executar ETL para um arquivo ZIP:
`python run.py etl data/input/seuarquivo.zip`
# Ou via Makefile (se o arquivo estiver em data/input/)
`make run_etl FILE=seuarquivo.zip`

Fazer uma consulta:

Bash

`python run.py query "Qual o fornecedor com o maior valor total de notas?"`
# Ou via Makefile
`make run_query QUERY="Qual o fornecedor com o maior valor total de notas?"`
Iniciar a API:

Bash

`python run.py start_api`
Iniciar o Streamlit:

Bash

`python run.py start_streamlit`
🧪 Testes
Bash

pytest
(Para rodar todos os testes automatizados.)

🧹 Limpeza
Para remover arquivos gerados (banco de dados, temporários, logs):

Bash

`make clean`