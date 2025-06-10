import os
from dotenv import load_dotenv
import re
import requests 
import json     

from .prompts import get_sql_generation_prompt

load_dotenv()
ollama_ready = False
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434/api")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "codellama") 

try:

    response = requests.get(f"{OLLAMA_API_BASE_URL}/tags", timeout=5) # Timeout para não travar
    response.raise_for_status()
    available_models = [m['name'].split(':')[0] for m in response.json().get('models', [])]
    if OLLAMA_MODEL_NAME not in available_models:
        print(f"Aviso: O modelo '{OLLAMA_MODEL_NAME}' não parece estar disponível no ollama local.")
        print(f"Modelos disponíveis: {', '.join(available_models) if available_models else 'Nenhum'}")
        print("Certifique-se de ter baixado o modelo com 'ollama run <nome_do_modelo>'")
    else:
        ollama_ready = True
        print(f"ollama cliente conectado e modelo '{OLLAMA_MODEL_NAME}' detectado.")
except requests.exceptions.ConnectionError:
    print(f"Erro: Não foi possível conectar ao ollama na URL '{OLLAMA_API_BASE_URL}'.")
    print("Certifique-se de que o aplicativo ollama está rodando em segundo plano.")
except Exception as e:
    print(f"Erro inesperado ao verificar o ollama: {e}")

def convert_natural_language_to_sql(
    user_query: str,
    db_schema: str,
    dialect: str = "MySQL"
) -> str | None:
    """
    Converte uma pergunta em linguagem natural para uma query SQL usando o LLM Llama via ollama.

    Args:
        user_query (str): A pergunta do usuário em linguagem natural.
        db_schema (str): O esquema do banco de dados formatado (obtido de schema_inspector.py).
        dialect (str): O dialeto SQL do banco de dados (ex: "MySQL", "PostgreSQL").

    Returns:
        str | None: A query SQL gerada ou None se houver um erro.
    """
    if not ollama_ready:
        print("ollama não está pronto ou conectado. Não é possível gerar SQL.")
        return None

    full_prompt = get_sql_generation_prompt(user_query, db_schema, dialect)

    try:
        # Payload para a API de geração do ollama
        payload = {
            "model": OLLAMA_MODEL_NAME,
            "prompt": full_prompt,
            "stream": False, # Queremos a resposta completa de uma vez
            "options": {
                "temperature": 0.1,    # Torna a saída mais determinística
                "num_predict": 500     # Max tokens para a saída
            }
        }
        
        # Envia a requisição POST para a API local do ollama
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{OLLAMA_API_BASE_URL}/generate", headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Lança um erro para status de erro (4xx ou 5xx)
        
        response_data = response.json()
        sql_query = response_data.get('response', '').strip()

        # Limpeza adicional: O LLM pode adicionar ```sql``` ou ;. Removemos para query pura.
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        sql_query = re.sub(r";\s*$", "", sql_query) # Remove ';' no final da string

        print(f"SQL Gerado:\n{sql_query}")
        return sql_query

    except requests.exceptions.RequestException as e:
        print(f"Erro de rede ou na API do ollama: {e}")
        print(f"Resposta do ollama: {response.text if 'response' in locals() else 'N/A'}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao chamar o ollama ou processar resposta: {e}")
        return None

# --- Teste de funcionalidade (opcional) ---
if __name__ == "__main__":
    from database.schema import get_database_schema, format_schema_for_llm
    from database.connection import get_mysql_engine, test_connection
    
    mysql_engine = None
    try:
        mysql_engine = get_mysql_engine()
        if not test_connection(mysql_engine):
            mysql_engine = None
    except ValueError as e:
        print(f"Erro de configuração MySQL: {e}")
    except Exception as e:
        print(f"Erro inesperado ao criar engine MySQL: {e}")

    if mysql_engine:
        db_schema_dict = get_database_schema(mysql_engine)
        if db_schema_dict:
            db_schema_str = format_schema_for_llm(db_schema_dict)
            print("\nEsquema do Banco de Dados para o LLM:")
            print(db_schema_str)

            user_question = "qual o nome de todos os alunos do professor Einstein?"

            print(f"\nPergunta do Usuário: '{user_question}'")
            generated_sql = convert_natural_language_to_sql(user_question, db_schema_str, "MySQL")

            if generated_sql:
                print(f"\nSQL Gerado pelo LLM via ollama:\n{generated_sql}")
                # Opcional: Executar a query gerada para ver os resultados
                # from ..database.connection import execute_query # Importe se precisar
                # results_df = execute_query(mysql_engine, generated_sql)
                # if results_df is not None:
                #     print("\nResultados da Query Executada:")
                #     print(results_df)
            else:
                print("\nFalha ao gerar SQL.")
        else:
            print("Não foi possível obter o esquema do MySQL para teste.")
    else:
        print("Não foi possível conectar ao MySQL para teste de LLM.")

    print("\n--- Fim do Teste de Conversão ---")