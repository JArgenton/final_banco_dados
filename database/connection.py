from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

def get_mysql_engine() -> Engine:
    """
    Cria e retorna uma engine SQLAlchemy para conexão MySQL.
    As credenciais são carregadas do arquivo .env.
    """
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST")
    port = os.getenv("MYSQL_PORT")
    db = os.getenv("MYSQL_DB")

    if not all([user, password, host, port, db]):
        raise ValueError("faltou info no .env mysql")

    # mysql+mysqlconnector://user:password@host:port/database
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

def test_connection(engine: Engine):

    try:
        with engine.connect() as connection:

            result = connection.execute(text("SELECT 1")) #select true, só da errado se nao carregou a db
            print(f"{engine.url.database} conectado")
            return True
    except Exception as e:
        print(f"FALHA EM {engine.url.database}: {e}")
        return False



#comentarios oxygen
def execute_query(engine, query, fetch_results=True):
    """
    Executa uma query SQL no banco de dados e retorna os resultados em um DataFrame do Pandas,
    ou None para queries que não retornam resultados (ex: INSERT, UPDATE, DELETE).

    Args:
        engine (Engine): A engine SQLAlchemy para o banco de dados (obtida de get_mysql_engine() ou get_postgresql_engine()).
        query (str): A string da query SQL a ser executada.
        fetch_results (bool): Se True, tenta buscar os resultados (para SELECT).
                              Se False, apenas executa (para INSERT/UPDATE/DELETE).

    Returns:
        pd.DataFrame | None: Um DataFrame do Pandas com os resultados da query, ou None.
    """
    try:
        with engine.connect() as connection:
            with connection.begin():
                if fetch_results:
                    df = pd.read_sql_query(query, connection)
                    print(f"Querry -> {len(df)}")
                    return df
                else:
                    # Para queries que modificam o banco (INSERT, UPDATE, DELETE, CREATE, DROP)
                    result = connection.execute(text(query)) # Usa text() para consultas não-parâmetros
                    print(f"Alteração feita: {result.rowcount}")
                    return None
    except Exception as e:
        print(f"Erro em query {e}")
        print(f"Query -> {query}")
        return None



if __name__ == "__main__":
    try:
        mysql_engine = get_mysql_engine()
        test_connection(mysql_engine)
    except ValueError as e:
        print(f"Erro MySQL: {e}")
    except Exception as e:
        print(f"Erro na engine MySQL: {e}")

    try:
        pgsql_engine = get_postgresql_engine()
        test_connection(pgsql_engine)
    except ValueError as e:
        print(f"Erro PostgreSQL: {e}")
    except Exception as e:
        print(f"Erro na engine PostgreSQL: {e}")
