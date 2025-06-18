import streamlit as st
import requests
import pandas as pd
from app.config import API_BASE_URL
from app.logger import logger  # Usar o logger do projeto

st.set_page_config(page_title="Consulta de Notas Fiscais com IA", layout="centered", icon="📊")

st.title("Consulta de Notas Fiscais com IA 📊")
st.markdown("""
Esta aplicação permite fazer upload de arquivos ZIP contendo dados de notas fiscais (cabeçalho e itens) 
e, em seguida, fazer perguntas em linguagem natural sobre esses dados.
""")

# --- Seção de Upload e Processamento ---
st.header("1. Upload e Processamento de Dados 📁")
uploaded_file = st.file_uploader("Faça upload de um arquivo ZIP com seus dados de notas fiscais", type="zip")

if uploaded_file is not None:
    st.info("Processando seu arquivo... Isso pode levar alguns segundos.")

    # Prepara o arquivo para envio via POST como multipart/form-data
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/zip")}

    try:
        response = requests.post(f"{API_BASE_URL}/upload-and-process/", files=files)

        if response.status_code == 200:
            st.success(f"🎉 {response.json().get('message', 'Arquivo processado com sucesso!')}")
            logger.info(f"Upload e processamento de {uploaded_file.name} bem-sucedidos.")
        else:
            error_detail = response.json().get("detail", "Erro desconhecido.")
            st.error(f"❌ Erro ao processar o arquivo: {error_detail}")
            logger.error(f"Erro da API em upload para {uploaded_file.name}: {error_detail}")
    except requests.exceptions.ConnectionError:
        st.error(f"🚫 Não foi possível conectar à API em {API_BASE_URL}. Verifique se a API está rodando.")
        logger.critical(f"Falha de conexão com a API em {API_BASE_URL}")
    except Exception as e:
        st.error(f"🚨 Erro inesperado durante o upload: {e}")
        logger.critical(f"Erro inesperado no Streamlit durante upload: {e}")

# --- Seção de Consulta ---
st.header("2. Consulte Seus Dados 💬")
question = st.text_input(
    "Digite sua pergunta sobre as notas fiscais (ex.: 'Qual o valor total da nota com a chave X?', 'Qual o fornecedor que mais vendeu?', 'Liste os itens da nota Y.').")

if st.button("Consultar Dados"):
    if question:
        st.info(f"Processando consulta: '{question}'...")
        try:
            params = {"question": question}
            response = requests.get(f"{API_BASE_URL}/query/", params=params)

            if response.status_code == 200:
                result_data = response.json()
                status_msg = result_data.get("status", "unknown")
                message_msg = result_data.get("message", "Nenhuma mensagem.")

                st.subheader("Resultado:")
                if status_msg == "success":
                    st.success(f"✅ {message_msg}")
                elif status_msg == "warning":
                    st.warning(f"⚠️ {message_msg}")
                else:  # Inclui 'info' e outros status
                    st.info(f"ℹ️ {message_msg}")

                data_records = result_data.get("data")
                if data_records:
                    try:
                        df_result = pd.DataFrame(data_records)
                        st.dataframe(df_result, use_container_width=True)  # Melhor visualização
                    except Exception as e:
                        st.error(f"Erro ao exibir dados: {e}. Raw data: {data_records}")
                        logger.error(f"Erro ao criar DataFrame para exibição: {e}", exc_info=True)
                else:
                    st.info("A consulta não retornou dados tabulares.")
                logger.info(f"Consulta '{question}' concluída com status: {status_msg}.")
            else:
                error_detail = response.json().get("detail", "Erro desconhecido.")
                st.error(f"❌ Erro ao consultar: {error_detail}")
                logger.error(f"Erro da API em consulta para '{question}': {error_detail}")
        except requests.exceptions.ConnectionError:
            st.error(f"🚫 Não foi possível conectar à API em {API_BASE_URL}. Verifique se a API está rodando.")
            logger.critical(f"Falha de conexão com a API em {API_BASE_URL}")
        except Exception as e:
            st.error(f"🚨 Erro inesperado durante a consulta: {e}")
            logger.critical(f"Erro inesperado no Streamlit durante consulta: {e}")
    else:
        st.warning("Por favor, digite uma pergunta para consultar.")

st.markdown("---")
st.markdown("Desenvolvido para o desafio de Agentes de IA. ©️ 2025")