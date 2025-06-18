import streamlit as st
import requests
import zipfile
import tempfile
import os
import sys
from pathlib import Path
import pandas as pd

# Adiciona a pasta raiz e a pasta app ao sys.path para imports funcionarem na nuvem
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
sys.path.append(str(BASE_DIR))
sys.path.append(str(APP_DIR))

from app.config import API_BASE_URL

st.set_page_config(page_title="Agente IA - Notas Fiscais", layout="wide")

st.title("📊 Agente Inteligente para Notas Fiscais")

st.markdown("Faça upload de um arquivo `.zip` contendo os arquivos CSV de cabeçalho e itens de notas fiscais.")

uploaded_file = st.file_uploader("📎 Upload do arquivo ZIP", type="zip")

if uploaded_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        csv_files = [f for f in os.listdir(tmpdir) if f.endswith(".csv")]
        if not csv_files:
            st.error("❌ Nenhum arquivo CSV encontrado no ZIP.")
        else:
            files = [
                ("files", (csv_file, open(os.path.join(tmpdir, csv_file), "rb"), "text/csv"))
                for csv_file in csv_files
            ]

            with st.spinner("Enviando arquivos para processamento..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/upload-and-process/",
                        files=files
                    )
                    if response.status_code == 200:
                        st.success("✅ Arquivos processados com sucesso!")
                    else:
                        st.error(f"❌ Erro na API: {response.text}")
                except Exception as e:
                    st.error(f"❌ Erro ao enviar arquivos: {str(e)}")

st.markdown("---")
st.subheader("❓ Faça sua pergunta sobre os dados:")

question = st.text_input("Exemplo: Qual fornecedor teve maior valor total?")

if question:
    with st.spinner("Consultando agente..."):
        try:
            response = requests.get(
                f"{API_BASE_URL}/query/",
                params={"question": question}
            )
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "info")
                message = result.get("message", "")
                data = result.get("data", [])

                if status == "success":
                    st.success(message)
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                elif status == "warning":
                    st.warning(message)
                else:
                    st.error(message)
            else:
                st.error(f"Erro: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Erro durante a consulta: {str(e)}")
