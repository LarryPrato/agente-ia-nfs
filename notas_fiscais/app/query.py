from collections import namedtuple
import pandas as pd
from langchain.agents import create_sql_agent
# Importa componentes específicos da LangChain para LLMs e utilitários de banco de dados
from langchain_community.llms import HuggingFacePipeline, LlamaCpp
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
# Importa pipeline do Transformers para modelos Hugging Face
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM  # Adicionado AutoTokenizer, AutoModelForCausalLM
# Importa variáveis de configuração e logger do diretório 'app' usando importação absoluta
from app.config import DB_PATH, ENV, LLM_CLOUD_MODEL_NAME, LLM_LOCAL_MODEL_PATH, HF_TOKEN
from app.logger import logger
import os
from huggingface_hub import login  # Adicionado para login explícito

# Define um namedtuple para padronizar o resultado das consultas
QueryResult = namedtuple("QueryResult", ["data", "status", "message"])

# Variável global para armazenar a instância do LLM (cache)
_llm_instance = None


def get_llm():
    """
    Inicializa e retorna uma instância do Large Language Model (LLM)
    baseado na variável de ambiente ENV (cloud ou local).
    O LLM é cacheado para evitar recarregamento em cada requisição.
    """
    global _llm_instance
    if _llm_instance is not None:
        logger.info("Retornando LLM do cache.")
        return _llm_instance

    if ENV == "cloud":
        logger.info(f"Carregando LLM da nuvem: {LLM_CLOUD_MODEL_NAME}")
        try:
            if not HF_TOKEN:
                raise ValueError("HF_TOKEN não definido. Necessário para acessar modelos Hugging Face na nuvem.")

            # Autentica no Hugging Face Hub (mesmo para modelos públicos, para evitar rate limits)
            login(token=HF_TOKEN)

            # Inicializa o tokenizer e o modelo para geração de texto
            # Usar AutoModelForCausalLM.from_pretrained com device_map="auto" para melhor uso de recursos
            tokenizer = AutoTokenizer.from_pretrained(LLM_CLOUD_MODEL_NAME, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                LLM_CLOUD_MODEL_NAME,
                trust_remote_code=True,
                device_map="auto",  # Permite que transformers use CPU/GPU automaticamente
                load_in_8bit=True  # Tentar carregar em 8-bit para economizar memória (requer bitsandbytes e accelerate)
            )

            # Cria um pipeline de geração de texto com o modelo carregado
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,  # Limita o número de novos tokens gerados
                temperature=0.01,  # Controla a aleatoriedade da saída (valores menores para mais determinismo)
                do_sample=True,  # Permite amostragem para diversidade
                top_k=50,  # Considera apenas os 50 tokens mais prováveis
                num_return_sequences=1,  # Retorna apenas uma sequência gerada
                # device=-1 foi removido para deixar device_map="auto" decidir
            )
            _llm_instance = HuggingFacePipeline(pipeline=pipe)  # Cache a instância
            return _llm_instance
        except Exception as e:
            logger.error(f"Erro ao carregar LLM da nuvem: {e}", exc_info=True)
            raise RuntimeError(f"Falha ao carregar LLM da nuvem: {e}. Verifique LLM_CLOUD_MODEL_NAME e HF_TOKEN.")
    else:
        logger.info(f"Carregando LLM local: {LLM_LOCAL_MODEL_PATH}")
        if not LLM_LOCAL_MODEL_PATH.exists():
            raise FileNotFoundError(f"Modelo local não encontrado em {LLM_LOCAL_MODEL_PATH}. "
                                    f"Certifique-se de baixar o modelo ou ajustar LLM_LOCAL_MODEL_PATH.")
        try:
            # Inicializa o modelo LlamaCpp para inferência local
            _llm_instance = LlamaCpp(  # Cache a instância
                model_path=str(LLM_LOCAL_MODEL_PATH),
                temperature=0.01,  # Controla a aleatoriedade
                max_tokens=256,  # Limite de tokens na resposta
                top_p=0.9,  # Amostragem de núcleo
                n_ctx=2048,  # Tamanho do contexto (número máximo de tokens de entrada)
                n_gpu_layers=0,  # Número de camadas a descarregar na GPU (0 para CPU)
                verbose=False  # Desativa logs verbosos do LlamaCpp
            )
            return _llm_instance
        except Exception as e:
            logger.error(f"Erro ao carregar LLM local: {e}", exc_info=True)
            raise RuntimeError(f"Falha ao carregar LLM local: {e}. Verifique model_path e dependências.")


def query_data(question: str) -> QueryResult:
    """
    Executa uma consulta em linguagem natural usando um agente de IA baseado em SQL.
    O agente interage com um banco de dados SQLite para obter as respostas.
    """
    logger.info(f"Consulta recebida para o agente: '{question}'")
    try:
        # Tenta obter uma instância do LLM (local ou cloud)
        llm = get_llm()

        # Conecta ao banco de dados SQLite
        db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
        # Obtém o esquema da tabela (importante para o agente entender a estrutura)
        table_info = db.get_table_info()

        if not table_info:
            logger.error("Banco de dados vazio ou sem esquema detectado.")
            return QueryResult(pd.DataFrame(), "error",
                               "Banco de dados vazio ou sem esquema. Carregue os dados primeiro.")

        # Define o prompt para o agente de IA, instruindo-o sobre seu papel e as regras
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""Você é um assistente de IA útil e analista de dados, especializado em notas fiscais. 
Use SQL baseado no esquema do banco de dados abaixo para responder às perguntas sobre a tabela `notas_fiscais`.

Esquema da Tabela `notas_fiscais`:
{table_info}

Regras para sua resposta:
1. Use funções SQL (SUM, AVG, COUNT, MAX, MIN) quando necessário para agregar dados.
2. Utilize os nomes exatos das colunas e tabelas como no esquema.
3. Forneça respostas em português claro, conciso e útil.
4. Se não houver dados relevantes, ou se a pergunta for impossível de responder com os dados fornecidos, diga "Não foi possível encontrar uma resposta" ou "Não tenho informações sobre isso".
5. Nunca mostre a query SQL gerada ou qualquer código. Apenas a resposta final.
6. Apresente os resultados de forma legível e formatada, se aplicável (ex: listar itens, valores, etc.).
7. Se a pergunta for sobre um valor monetário, formate a resposta com duas casas decimais e o símbolo "R$".
"""),
            HumanMessage(content="{input}")  # A pergunta do usuário será injetada aqui
        ])

        # Cria o agente SQL.
        # "openai-tools" é um tipo de agente que funciona bem com LLMs que podem usar ferramentas.
        # verbose=False para não mostrar o processo interno do agente (queries SQL, etc.)
        # handle_parsing_errors=True para que o agente tente se recuperar de erros de parsing.
        agent_executor = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="openai-tools",  # Pode ser "zero-shot-react-description" ou outros também
            verbose=False,
            handle_parsing_errors=True,
            prompt=prompt
        )

        # Invoca o agente com a pergunta do usuário
        agent_response = agent_executor.invoke({"input": question})
        # Extrai a resposta final do agente. Pode ser 'output' ou a representação string.
        final_answer = agent_response.get("output", str(agent_response))
        status = "success"  # Status inicial como sucesso

        # Verifica se a resposta do agente indica que não encontrou ou houve um problema
        if any(term in final_answer.lower() for term in
               ["não foi possível encontrar uma resposta", "não tenho informações", "erro", "não encontrei",
                "não sei"]):
            status = "warning" if "não" in final_answer.lower() else "error"

        # Retorna a resposta em um DataFrame (mesmo que seja uma string única) para consistência
        df = pd.DataFrame({"Resposta": [final_answer]})
        logger.info(f"Consulta finalizada. Status: {status}, Mensagem: {final_answer[:100]}...")  # Log da resposta
        return QueryResult(df, status, final_answer)

    except Exception as e:
        logger.error(f"Erro inesperado durante a consulta ao agente: {e}", exc_info=True)
        return QueryResult(pd.DataFrame(), "error", f"Erro interno durante a consulta: {e}")