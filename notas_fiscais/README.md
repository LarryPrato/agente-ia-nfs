# 🤖 Agente Inteligente para Notas Fiscais (Desafio TCU)

Este projeto usa inteligência artificial para responder perguntas sobre notas fiscais a partir de arquivos CSV, utilizando LLMs via LangChain e Streamlit.

---

## 📦 Funcionalidades

- 📁 Upload de arquivos ZIP contendo cabeçalho e itens das NFs
- 🧠 Consultas em linguagem natural usando LLM
- 🧮 Processamento, limpeza e carga dos dados em SQLite
- 🌐 Interface amigável via Streamlit

---

## 🚀 Como Rodar Localmente

### 1. Clone o projeto e instale dependências
bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
pip install -r requirements.txt
2. Configure o ambiente .env
env
Copiar
Editar
ENV=cloud
LLM_CLOUD_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
HF_TOKEN=seu_token_huggingface
API_BASE_URL=http://localhost:8000
3. Rode a API
bash
Copiar
Editar
python run.py start_api
4. Rode o app Streamlit
bash
Copiar
Editar
python run.py start_streamlit
☁️ Deploy no Streamlit Cloud
Suba seu projeto no GitHub

Acesse https://share.streamlit.io

Crie um novo app e aponte para interface/streamlit_app.py

Vá em Settings > Secrets e adicione:

toml
Copiar
Editar
ENV = "cloud"
LLM_CLOUD_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
HF_TOKEN = "seu_token_huggingface"
API_BASE_URL = "https://sua-api-no-render.com"
❓ Exemplos de perguntas
Qual fornecedor recebeu maior valor total?

Qual item teve maior quantidade entregue?

Quantas notas foram emitidas por fornecedor X?

Qual o valor médio das notas?

🧰 Tecnologias
LangChain

Streamlit

FastAPI

Hugging Face Transformers

SQLite

🔐 Segurança
.env não é versionado (.gitignore protege)

Em ambiente cloud, use secrets.toml para proteger tokens

🛠️ Estrutura
arduino
Copiar
Editar
.
├── app/
│   ├── config.py
│   ├── query.py
│   ├── logger.py
│   └── ...
├── interface/
│   └── streamlit_app.py
├── data/
├── run.py
├── run_etl.py
├── requirements.txt
└── README.md
