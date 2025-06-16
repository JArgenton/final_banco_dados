from sqlalchemy import create_engine, inspect, MetaData, Table, Column, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
import re
import json 
import pandas as pd 
import google.generativeai as genai 
import requests
from typing import Dict, List

from database.connection import get_db_engine, test_connection, execute_query
from database.schema import get_database_schema, format_schema_for_llm
from text_to_sql.prompts import get_sql_generation_prompt

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_ready = False

OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME") 
ollama_ready = False

llm_provider = os.getenv("LLM").upper() 
if llm_provider == "GEMINI":
    print("USANDO GEMINI")
    try:
        if not GEMINI_API_KEY:
            raise ValueError(".env nao tem GEMINI_API_KEY")
        
        genai.configure(api_key=GEMINI_API_KEY)
        transport="rest", 
        client_options={"api_endpoint": "generativelanguage.googleapis.com"}
        list(genai.list_models()) 
        gemini_ready = True
        print(f"Gemini OK")
    except Exception as e:
        gemini_ready = False
        print(f"Erro Gemini: Não foi possível conectar {e}")
        exit(1) 
elif llm_provider == "OLLAMA":
    print("USANDO OLLAMA")
    try:
        response = requests.get(f"{OLLAMA_API_BASE_URL}/tags", timeout=5)
        response.raise_for_status()
        ollama_ready = True
        print(f"Ollama OK - {OLLAMA_MODEL_NAME}")
    except Exception as e:
        ollama_ready = False
        print(f"Erro Ollama: Não foi possível conectar {e}")
        exit(1)
else:
    print(f"Erro: LLM '{llm_provider}' inválido no .env.")
    exit(1)

def convert_natural_language_to_sql(user_query: str, db_schema: str, dialect: str = "MySQL") -> str | None:
    if llm_provider == "GEMINI":
        if not gemini_ready:
            print("ERRO GEMINI")
            return None
        full_prompt = get_sql_generation_prompt(user_query, db_schema, dialect)
        try:
            model = genai.GenerativeModel('models/gemini-2.0-flash-lite') 
            response = model.generate_content(full_prompt,generation_config=genai.GenerationConfig(temperature=0.1, max_output_tokens=500))

            sql_query = response.text.strip()

            sql_query = re.sub(r"```sql|```|;\s*$", "", sql_query, flags=re.IGNORECASE).strip()

            print(f"SQL Gerado (Gemini):\n{sql_query}")

            return sql_query
        except Exception as e:
            print(f"Erro ao chamar o Gemini {e}")
            return None
    
    elif llm_provider == "OLLAMA":
        if not ollama_ready:
            print("ERRO OLLAMA")
            return None
        full_prompt = get_sql_generation_prompt(user_query, db_schema, dialect)
        try:
            payload = {
                "model": OLLAMA_MODEL_NAME,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 500
                }
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{OLLAMA_API_BASE_URL}/generate", headers=headers, data=json.dumps(payload))
            response.raise_for_status() 
            sql_query = response.json().get('response', '').strip()
            sql_query = re.sub(r"```sql|```|;\s*$", "", sql_query, flags=re.IGNORECASE).strip()

            print(f"SQL Gerado (Qwen/Ollama):\n{sql_query}")

            return sql_query
        except requests.exceptions.RequestException as e:

            print(f"Erro (Ollama): Falha na comunicação com Ollama: {e}")
            return None
        except Exception as e:
            print(f"Erro Ollama: Ocorreu um problema ao gerar SQL. {e}")
            return None
    
    return None