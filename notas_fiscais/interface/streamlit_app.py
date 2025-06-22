import streamlit as st
import requests
import os
import sys
from pathlib import Path
import pandas as pd
import logging

# Adiciona o diretório raiz do projeto ao sys.path para importações relativas funcionarem
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.config import get_env_var
API_BASE_URL = get_env_var("API_BASE_URL")


# --- Configuração Inicial do Streamlit ---
st.set_page_config(
    page_title="Agente IA - Notas Fiscais",
    layout="wide",  # Usa a largura máxima da página
    initial_sidebar_state="auto"  # Define o estado inicial da barra lateral
)

# --- Título e Descrição da Aplicação ---
st.title("📊 Agente Inteligente para Consulta de Notas Fiscais")
st.markdown("""
Bem-vindo ao Agente IA de Notas Fiscais!

1.  **Faça upload de um arquivo ZIP** contendo `Cabecalho.csv` e `Itens.csv`.
2.  **Envie suas perguntas** em linguagem natural sobre os dados carregados.
""")

# --- Seção de Upload de Arquivos ---
st.subheader("📎 Upload do Arquivo ZIP das Notas Fiscais")
uploaded_file = st.file_uploader(
    "Por favor, selecione um arquivo `.zip` contendo os CSVs de cabeçalho e itens.",
    type="zip",
    accept_multiple_files=False  # Apenas um arquivo por vez
)

# Botão de processamento do upload
if uploaded_file:
    # Usar um st.form para agrupar o upload e o botão, permitindo mais controle sobre o state
    with st.form("upload_form"):
        st.write(f"Arquivo selecionado: **{uploaded_file.name}**")
        submit_upload = st.form_submit_button("Processar Arquivo ZIP")

        if submit_upload:
            if not uploaded_file.name.endswith(".zip"):
                st.error("❌ Apenas arquivos `.zip` são permitidos. Por favor, selecione um arquivo ZIP válido.")
            else:
                with st.spinner(
                        f"Enviando e processando '{uploaded_file.name}' na API... Isso pode levar alguns momentos."):
                    try:
                        # Prepara o arquivo para envio. 'files' deve ser um dicionário onde a chave
                        # é o nome do parâmetro esperado pela API ('file') e o valor é uma tupla
                        # (nome do arquivo, conteúdo binário, tipo de conteúdo).
                        # A API espera um único arquivo com o nome 'file'.
                        files = {
                            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                        }

                        # Faz a requisição POST para o endpoint de upload da API
                        response = requests.post(
                            f"{API_BASE_URL}/upload/",
                            files=files,
                            timeout=600  # Aumenta o timeout para 10 minutos para processamentos longos
                        )

                        # Verifica o status da resposta da API
                        if response.status_code == 200:
                            st.success(
                                f"✅ Arquivo '{uploaded_file.name}' processado com sucesso! Agora você pode fazer perguntas.")
                            logger.info(
                                f"Upload e processamento de {uploaded_file.name} via API concluído com sucesso.")
                        else:
                            st.error(
                                f"❌ Erro ao processar o arquivo na API: `{response.status_code}` - `{response.text}`")
                            logger.error(f"Erro da API no upload: {response.status_code} - {response.text}")
                    except requests.exceptions.ConnectionError as e:
                        st.error(
                            f"❌ Não foi possível conectar à API. Verifique se ela está online e a `API_BASE_URL` está correta. Detalhes: `{e}`")
                        logger.critical(f"ConnectionError ao acessar API: {e}")
                    except requests.exceptions.Timeout:
                        st.error(
                            "❌ O processamento do arquivo excedeu o tempo limite. Tente novamente ou use um arquivo menor.")
                        logger.error("Timeout ao processar arquivo na API.")
                    except Exception as e:
                        st.error(f"❌ Ocorreu um erro inesperado durante o upload: `{str(e)}`")
                        logger.critical(f"Erro inesperado no Streamlit durante upload: {e}", exc_info=True)

st.markdown("---")  # Separador visual

# --- Seção de Consulta ao Agente ---
st.subheader("❓ Faça sua Pergunta sobre os Dados")
question = st.text_input(
    "Digite sua pergunta aqui (ex: 'Qual o fornecedor com maior valor total de notas?', 'Qual item teve maior quantidade entregue?').",
    placeholder="Ex: Qual fornecedor recebeu o maior montante total?"
)

# Botão para enviar a pergunta
if st.button("Perguntar ao Agente"):
    if not question:
        st.warning("Por favor, digite uma pergunta antes de clicar em 'Perguntar'.")
    else:
        with st.spinner("Consultando o agente de IA... Isso pode levar alguns instantes para LLMs maiores."):
            try:
                # Faz a requisição GET para o endpoint de consulta da API
                response = requests.get(
                    f"{API_BASE_URL}/query/",
                    params={"question": question},
                    timeout=300  # Aumenta o timeout para 5 minutos
                )

                # Verifica o status da resposta da API
                if response.status_code == 200:
                    result = response.json()
                    status_api = result.get("status", "info")
                    message = result.get("message") or result.get("answer") or "Nenhuma resposta recebida da API."
                    data = result.get("data", [])  # Espera uma lista de dicionários para os dados
                    result = response.json() #######
                    message = result["message"] #######
                    
                    if message.startswith('|'): #######
                        #st.markdown("### 📋 Resultado Tabular") #######
                        st.markdown(message, unsafe_allow_html=True) #######
                    else: #######
                        st.success(f"✅Resposta do Agente: {message}") #######
                    # '''
                    # ###<-
                    # if status_api == "success":
                    #     message = result["message"]
                    #     if message.strip().startswith('|'):
                    #         #st.markdown("### 📋 Resultado Tabular")
                    #         st.markdown(message, unsafe_allow_html=True)
                    #     else:
                    #         st.success(f"✅ Resposta do Agente {message}")
                    # elif status_api == "warning":
                    #     st.warning(f"⚠️ {message}")
                    # else:
                    #     st.error(f"❌ {message}")
                    # ###<-
                    # '''
                    # if status_api == "success":
                    #     st.markdown("### 📋 Resposta do Agente")
                    #     st.markdown(message, unsafe_allow_html=True)
                    #     logger.info(f"Consulta bem-sucedida: {message[:100]}...")
                    # elif status_api == "warning":
                    #     st.warning(f"⚠️ Atenção do Agente: {message}")
                    #     if data:
                    #         df = pd.DataFrame(data)
                    #         st.dataframe(df, use_container_width=True)
                    #     logger.warning(f"Consulta com alerta: {message[:100]}...")
                    # else:  # status_api == "error" ou outro
                    #     st.error(f"❌ O Agente encontrou um problema: {message}")
                    #     logger.error(f"Erro do agente na consulta: {message}")
                else:
                    st.error(f"❌ Erro na comunicação com a API: Código {response.status_code} - {response.text}")
                    logger.error(f"Erro da API na consulta: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError as e:
                st.error(f"❌ Não foi possível conectar à API de consulta. Detalhes: `{e}`")
                logger.critical(f"ConnectionError ao consultar API: {e}")
            except requests.exceptions.Timeout:
                st.error(
                    "❌ A consulta ao agente excedeu o tempo limite. A pergunta pode ser muito complexa ou o modelo está lento.")
                logger.error("Timeout ao consultar o agente.")
            except Exception as e:
                st.error(f"❌ Ocorreu um erro inesperado durante a consulta: `{str(e)}`")
                logger.critical(f"Erro inesperado no Streamlit durante consulta: {e}", exc_info=True)
