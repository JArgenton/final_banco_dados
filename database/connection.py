from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ProgrammingError
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

def get_mysql_engine() -> Engine:
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST")
    port = os.getenv("MYSQL_PORT")
    db = os.getenv("MYSQL_DB")

    if not all([user, password, host, port, db]):
        raise ValueError("faltou info no .env mysql")

    connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"
    return create_engine(connection_string)

def get_postgresql_engine() -> Engine:
    user = os.getenv("PGSQL_USER")
    password = os.getenv("PGSQL_PASSWORD")
    host = os.getenv("PGSQL_HOST")
    port = os.getenv("PGSQL_PORT")
    db = os.getenv("PGSQL_DB")

    if not all([user, password, host, port, db]):
        raise ValueError("faltou info no .env pgadm")

    connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(connection_string)

def get_db_engine(db_type: str) -> Engine:
    db_type_upper = db_type.upper()
    if db_type_upper == "MYSQL":
        return get_mysql_engine()
    elif db_type_upper == "POSTGRESQL":
        return get_postgresql_engine()
    else:
        raise ValueError(f"Tipo de banco de dados inválido no .env: '{db_type}'. Use 'MYSQL' ou 'POSTGRESQL'.")

def test_connection(engine: Engine):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print(f"{engine.url.database} conectado")
            return True
    except OperationalError as e:
        print(f"FALHA EM {engine.url.database}: {e}")
        print("Verifique se o banco de dados está rodando e as credenciais estão corretas no .env.")
        return False
    except Exception as e:
        print(f"ERRO INESPERADO AO TESTAR CONEXÃO COM {engine.url.database}: {e}")
        return False

def execute_query(engine: Engine, query: str, fetch_results: bool = True) -> pd.DataFrame | str | None:
    try:
        with engine.connect() as connection:
            with connection.begin():
                if fetch_results:
                    df = pd.read_sql_query(query, connection)
                    print(f"Querry -> {len(df)}")
                    return df
                else:
                    result = connection.execute(text(query))
                    if result.rowcount is not None:
                        print(f"Alteração feita: {result.rowcount}")
                        return f"Query executada com sucesso. Linhas afetadas: {result.rowcount}"
                    else:
                        print("Query de modificação executada com sucesso (linhas afetadas não aplicáveis/retornadas).")
                        return "Query de modificação executada com sucesso."
    except ProgrammingError as e:
        print(f"Erro em query {e}")
        print(f"Query -> {query}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao executar query: {e}")
        print(f"Query -> {query}")
        return None


if __name__ == "__main__":
    print("--- Testando Conexões de Banco de Dados ---")

    db_type_mysql = "MYSQL"
    try:
        mysql_engine_test = get_db_engine(db_type_mysql)
        test_connection(mysql_engine_test)
    except ValueError as e:
        print(f"Erro de configuração MySQL: {e}")
    except Exception as e:
        print(f"Erro na engine MySQL: {e}")
    print("----------------------------------------")

    db_type_pgsql = "POSTGRESQL"
    try:
        pgsql_engine_test = get_db_engine(db_type_pgsql)
        test_connection(pgsql_engine_test)
    except ValueError as e:
        print(f"Erro de configuração PostgreSQL: {e}")
    except Exception as e:
        print(f"Erro na engine PostgreSQL: {e}")
    print("----------------------------------------")