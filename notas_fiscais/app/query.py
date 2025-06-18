from collections import namedtuple
import pandas as pd
import os
from langchain.agents import create_sql_agent
from langchain_community.llms import HuggingFacePipeline, LlamaCpp
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from transformers import pipeline
from config import DB_PATH, ENV, LLM_CLOUD_MODEL_NAME, LLM_LOCAL_MODEL_PATH
from logger import logger

QueryResult = namedtuple("QueryResult", ["data", "status", "message"])

def get_llm():
    """Inicializa e retorna o LLM da Hugging Face (cloud) ou local (LlamaCpp)."""
    if ENV == "cloud":
        try:
            hf_token = os.getenv("HF_TOKEN")
            if not hf_token:
                raise ValueError("HF_TOKEN não definido no .env")

            pipe = pipeline(
                "text-generation",
                model=LLM_CLOUD_MODEL_NAME,
                use_auth_token=hf_token,
                max_new_tokens=512,
                temperature=0.01,
                device=-1
            )
            return HuggingFacePipeline(pipeline=pipe)
        except Exception as e:
            logger.error(f"Erro ao configurar LLM cloud: {e}", exc_info=True)
            raise RuntimeError(f"Erro ao carregar LLM cloud: {e}")
    else:
        if not LLM_LOCAL_MODEL_PATH.exists():
            raise FileNotFoundError(f"Modelo local não encontrado em {LLM_LOCAL_MODEL_PATH}")
        try:
            return LlamaCpp(
                model_path=str(LLM_LOCAL_MODEL_PATH),
                temperature=0.01,
                max_tokens=256,
                top_p=0.9,
                n_ctx=2048,
                n_gpu_layers=0,
                verbose=False
            )
        except Exception as e:
            logger.error(f"Erro ao carregar LLM local: {e}", exc_info=True)
            raise RuntimeError(f"Erro ao carregar LLM local: {e}")

def query_data(question: str) -> QueryResult:
    logger.info(f"Consulta recebida: '{question}'")
    try:
        llm_instance = get_llm()
        db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
        table_info = db.get_table_info()

        if not table_info:
            return QueryResult(pd.DataFrame(), "error", "Banco de dados vazio ou esquema não acessível.")

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""Você é um assistente de IA útil e um analista de dados. 
Você interage com um usuário fazendo perguntas sobre dados de notas fiscais armazenados em um banco de dados SQLite.
O banco de dados contém uma tabela chamada `notas_fiscais` com as seguintes colunas e suas descrições:
{table_info}

Ao responder a perguntas, você deve:
1.  Sempre tente gerar uma consulta SQL para responder à pergunta.
2.  Use os nomes das colunas exatamente como estão no esquema.
3.  Se a pergunta solicitar dados agregados (ex: soma, média, contagem), use as funções de agregação SQL apropriadas (SUM, AVG, COUNT).
4.  Se a query SQL não retornar dados, informe o usuário de forma amigável.
5.  Sempre forneça uma resposta clara, concisa e diretamente relacionada à pergunta, em português.
6.  Se a pergunta for ambígua ou exigir mais informações, peça clareza ao usuário.
7.  Nunca mostre a query SQL gerada.
8.  **Retorne apenas a resposta final em linguagem natural, sem incluir a query SQL gerada explicitamente.**

Exemplos de perguntas e respostas esperadas:
- "Qual o valor total de todas as notas?" -> "O valor total de todas as notas é X."
- "Quantas notas foram emitidas pelo fornecedor 'ABC'?" -> "O fornecedor 'ABC' emitiu Y notas."
- "Qual o produto mais vendido em quantidade?" -> "O produto mais vendido em quantidade é 'Produto Z'."

Não adivinhe. Se você não conseguir responder com base nos dados e ferramentas disponíveis, diga que não sabe.
"""),
            ,
            HumanMessage(content="{input}")
        ])

        agent_executor = create_sql_agent(
            llm=llm_instance,
            db=db,
            agent_type="openai-tools",
            verbose=False,
            handle_parsing_errors=True,
            prompt=prompt
        )

        agent_response = agent_executor.invoke({"input": question})
        final_answer = agent_response.get("output", str(agent_response))
        status = "success"

        if any(k in final_answer.lower() for k in ["não encontrei", "não sei", "erro"]):
            status = "warning" if "não" in final_answer.lower() else "error"

        df_result = pd.DataFrame({"Resposta": [final_answer]})
        return QueryResult(df_result, status, final_answer)

    except Exception as e:
        logger.error(f"Erro durante consulta: {e}", exc_info=True)
        return QueryResult(pd.DataFrame(), "error", f"Erro ao processar a consulta: {e}")