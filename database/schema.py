from sqlalchemy import create_engine, inspect, MetaData, Table, Column
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Any
from .connection import get_mysql_engine, get_postgresql_engine, test_connection, execute_query

def get_database_schema(engine: Engine) -> Dict[str, List[Dict[str, str]]] | None:

    try:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        schema_info: Dict[str, List[Dict[str, str]]] = {}

        for table_name, table in metadata.tables.items():
            schema_info[table_name] = [
                {"name": column.name, "type": str(column.type)}
                for column in table.columns
            ]

        print(f"Esquema '{engine.url.database}' carregado")
        return schema_info

    except SQLAlchemyError as e:
        print(f"Erro esquema '{engine.url.database}': {e}")
        return None
    except Exception as e:
        print(f"Erro ao inspecionar o esquema: {e}")
        return None

def format_schema_for_llm(schema: Dict[str, List[Dict[str, str]]]) -> str:

    if not schema:
        return "<schema>Invalid schema</schema>"

    xml = "<schema>\n"
    for table_name, columns in schema.items():
        xml += f"  <table name=\"{table_name}\">\n"
        for col in columns:
            xml += f"    <column name=\"{col['name']}\" type=\"{col['type']}\" />\n"
        xml += f"  </table>\n"
    xml += "</schema>"

    return xml

