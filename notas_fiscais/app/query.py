from collections import namedtuple
import pandas as pd
from langchain.agents import create_sql_agent
from langchain_community.llms import HuggingFacePipeline, LlamaCpp
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from transformers import pipeline
from app.config import DB_PATH, ENV, LLM_CLOUD_MODEL_NAME, LLM_LOCAL_MODEL_PATH, HF_TOKEN
from app.logger import logger

QueryResult = namedtuple("QueryResult", ["data", "status", "message"])

def get_llm():
    """Inicializa o modelo Mistral 7B (cloud) ou Llama (local)."""
    if ENV == "cloud":
        try:
            if not HF_TOKEN:
                raise ValueError("HF_TOKEN não definido.")
            pipe = pipeline(
                "text-generation",
                model=LLM_CLOUD_MODEL_NAME,
                use_auth_token=HF_TOKEN,
                max_new_tokens=512,
                temperature=0.01,
                device=-1
            )
            return HuggingFacePipeline(pipeline=pipe)
        except Exception as e:
            logger.error(f"Erro ao carregar LLM cloud: {e}", exc_info=True)
            raise RuntimeError(f"Falha ao carregar LLM cloud: {e}")
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
            logger.error(f"Erro LLM local: {e}", exc_info=True)
            raise RuntimeError(f"Falha ao carregar LLM local: {e}")

def query_data(question: str) -> QueryResult:
    logger.info(f"Consulta recebida: '{question}'")
    try:
        llm = get_llm()
        db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
        table_info = db.get_table_info()
        if not table_info:
            return QueryResult(pd.DataFrame(), "error", "Banco de dados vazio ou sem esquema.")

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""Você é um assistente de IA útil e analista de dados. 
Use SQL baseado no esquema abaixo para responder às perguntas sobre a tabela `notas_fiscais`.

Esquema:
{table_info}

Regras:
1. Use funções SQL (SUM, AVG, COUNT) quando necessário.
2. Utilize nomes de colunas exatamente como no esquema.
3. Dê respostas em português, objetivas e úteis.
4. Se não souber ou não houver dados, diga isso.
5. Nunca mostre a query SQL gerada.
6. Responda apenas com texto final ao usuário.
"""),
            HumanMessage(content="{input}")
        ])

        agent_executor = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="openai-tools",
            verbose=False,
            handle_parsing_errors=True,
            prompt=prompt
        )

        agent_response = agent_executor.invoke({"input": question})
        final_answer = agent_response.get("output", str(agent_response))
        status = "success"

        if any(term in final_answer.lower() for term in ["não encontrei", "não sei", "erro"]):
            status = "warning" if "não" in final_answer.lower() else "error"

        df = pd.DataFrame({"Resposta": [final_answer]})
        return QueryResult(df, status, final_answer)

    except Exception as e:
        logger.error(f"Erro durante a consulta: {e}", exc_info=True)
        return QueryResult(pd.DataFrame(), "error", f"Erro durante a consulta: {e}")
