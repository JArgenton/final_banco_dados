from sqlalchemy import create_engine, inspect, MetaData, Table, Column
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Any

from .connection import get_mysql_engine, get_postgresql_engine, test_connection, execute_query


#esse padrao de comentario gera um arquivo de documentacao automatica
def get_database_schema(engine: Engine) -> Dict[str, List[Dict[str, str]]] | None:
    """
    Carrega o esquema de um banco de dados (tabelas/colunas)

    Args:
        engine (Engine): Obj sqlachemy

    Returns:
        Dict[str, List[Dict[str, str]]]: Um dicionário onde as chaves são nomes de tabelas,
                                        e os valores são listas de dicionários, cada um
                                        representando uma coluna com 'name' e 'type'.

    Exemplo de retorno:
    {
        "users": [
            {"name": "id", "type": "INTEGER"},
            {"name": "name", "type": "VARCHAR"},
            {"name": "age", "type": "INTEGER"}
        ],
        "products": [
            {"name": "product_id", "type": "INTEGER"},
            {"name": "product_name", "type": "VARCHAR"},
            {"name": "price", "type": "NUMERIC"}
        ]
    }
    """
    try:
        metadata = MetaData()
        
        metadata.reflect(bind=engine)#"importa" o banco pro obj

        schema_info: Dict[str, List[Dict[str, str]]] = {}
        for table_name, table in metadata.tables.items():
            columns_info: List[Dict[str, str]] = []
            for column in table.columns:
                columns_info.append({
                    "name": column.name,
                    "type": str(column.type) # Converte o tipo do SQLAlchemy para string
                })
            schema_info[table_name] = columns_info
        
        print(f"Esquema '{engine.url.database}' carregado")
        return schema_info

    except SQLAlchemyError as e:
        print(f"Erro esquema '{engine.url.database}': {e}")
        return None
    except Exception as e:
        print(f"Erro ao inspecionar o esquema: {e}")
        return None

#ideia do gemini, segundo ele é dificil um llm entender o obj q nos tinhamos
def format_schema_for_llm(schema: Dict[str, List[Dict[str, str]]]) -> str:
    """
    Formata o esquema do banco de dados em uma string legível para um LLM.

    Args:
        schema (Dict): O dicionário de esquema retornado por get_database_schema.

    Returns:
        str: Uma string formatada descrevendo o esquema.
    """
    if not schema:
        return "esquema invalido"

    formatted_string = "Esquema do Banco de Dados:\n"
    for table_name, columns in schema.items():
        formatted_string += f"- Tabela: {table_name}\n"
        for col in columns:
            formatted_string += f"  - Coluna: {col['name']} (Tipo: {col['type']})\n"
    return formatted_string

if __name__ == "__main__":
    print("--- Testando Inspeção de Esquema ---")

    # Testando MySQL
    try:
        mysql_engine = get_mysql_engine()
        if test_connection(mysql_engine):
            mysql_schema = get_database_schema(mysql_engine)
            if mysql_schema:
                print("\nEsquema MySQL Bruto:")
                # print(mysql_schema) # Descomente para ver o dicionário completo
                print("\nEsquema MySQL Formatado para LLM:")
                print(format_schema_for_llm(mysql_schema))
    except ValueError as e:
        print(f"Erro de configuração MySQL: {e}")
    except Exception as e:
        print(f"Erro inesperado no teste de esquema MySQL: {e}")

    try:
        pgsql_engine = get_postgresql_engine()
        if test_connection(pgsql_engine):
            pgsql_schema = get_database_schema(pgsql_engine)
            if pgsql_schema:
                print("\nEsquema PostgreSQL Bruto:")
                # print(pgsql_schema) # Descomente para ver o dicionário completo
                print("\nEsquema PostgreSQL Formatado para LLM:")
                print(format_schema_for_llm(pgsql_schema))
    except ValueError as e:
        print(f"Erro de configuração PostgreSQL: {e}")
    except Exception as e:
        print(f"Erro inesperado no teste de esquema PostgreSQL: {e}")

    #tenta querry
    try:
        execute_query(mysql_engine, "SELECT * FROM student", fetch_results=True)
    except Exception as e:
        print(f"Erro ao executar query MySQL: {e}")