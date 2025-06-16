# main_app.py
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
from text_to_sql.converter import convert_natural_language_to_sql # Assuming this is the unified converter


print("----------------------------------------------------------------------------")
print("TEXT TO SQL")

def main():
    db_engine = None
    db_type = os.getenv("DB_TYPE", "MYSQL").upper() # Padrão MYSQL no .env
    dialect = "MySQL" #PostgreSQL | MySQL

    try:
        db_engine = get_db_engine(db_type)
        if not test_connection(db_engine):
            db_engine = None
        else:
            if db_type == "POSTGRESQL":
                dialect = "PostgreSQL" 

            print(f"Conectado com engine {db_engine.url.database} ({db_type}).")
            print("----------------------------------------------------------------------------")

    except ValueError as e:
        print(f"ERRO DE CONFIGURAÇÃO DO BD ({db_type}): {e}")
        db_engine = None
    except Exception as e:
        print(f"ERRO AO INICIALIZAR ENGINE DO BANCO DE DADOS: {e}")
        db_engine = None

    if db_engine:
        print("OBTENDO SCHEMA")
        db_schema_dict = get_database_schema(db_engine)
        
        if db_schema_dict:
            db_schema_str = format_schema_for_llm(db_schema_dict)
            
            while True:
                user_question = input("pergunta (ou 'sair' para encerrar): ")
                
                if user_question.lower() == 'sair':
                    print("Encerrando a aplicação.")
                    break # Sai do loop se o usuário digitar 'sair'

                print(f"\nPergunta: {user_question}")
                
                generated_sql = convert_natural_language_to_sql(user_question, db_schema_str, dialect)
                
                if generated_sql:
                    print(f"\nSQL Gerado pelo LLM:\n{generated_sql}")
                    print("\nExecutando query")
                    print("----------------------------------------------------------------------------")
                    result = execute_query(db_engine, generated_sql, fetch_results=True)
                    
                    if result is not None:
                        print("\nResultados da Query Executada:")
                        # Adaptação para resultados com cabeçalho (primeira linha são as colunas)
                        if isinstance(result, list) and result and isinstance(result[0], tuple) and len(result) > 1:
                            columns = result[0]
                            data = result[1:]
                            if data: # Só tenta criar DataFrame se houver dados
                                print(pd.DataFrame(data, columns=columns))
                            else:
                                print("Nenhum resultado retornado pela query (mas a query foi executada).")
                        elif isinstance(result, list) and not result: # Lista vazia (ex: SELECT que retorna 0 linhas)
                            print("Nenhum resultado retornado pela query.")
                        else: # Para outros formatos ou quando execute_query já formata (ex: string de sucesso)
                            print(result)
                    else:
                        print("A query não retornou resultados ou falhou na execução.")
                else:
                    print("\nFalha ao gerar SQL. Verifique os logs acima para detalhes do LLM.")
                
                # Pergunta se o usuário deseja fazer mais queries
                continue_query = input("\nDeseja fazer outra query? (sim/não): ").lower()
                if continue_query != 'sim':
                    print("Encerrando a aplicação.")
                    break # Sai do loop se a resposta não for 'sim'
            
        else:
            print("Não foi possível obter o esquema do banco de dados.")
    else:
        print("Não foi possível conectar ao banco de dados. Verifique suas configurações e o status do servidor.")


if __name__ == "__main__":
    main()