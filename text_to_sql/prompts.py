def get_sql_generation_prompt(user_query: str, db_schema: str, dialect: str) -> str:
    """
    Gera o prompt completo para o LLM converter uma pergunta em linguagem natural para SQL.

    Args:
        user_query (str): A pergunta do usuário em linguagem natural.
        db_schema (str): A representação formatada do esquema do banco de dados.
        dialect (str): O dialeto SQL desejado (ex: "MySQL" ou "PostgreSQL").

    Returns:
        str: O prompt completo para o LLM.
    """
    # É importante instruir o LLM sobre o dialeto SQL e o formato de saída desejado.
    # Também pedimos para ele explicar a query, o que pode ser útil para depuração e aprendizado.
    prompt = f"""
Você é um assistente de inteligência artificial especializado em converter perguntas em linguagem natural para queries SQL.
Você deve gerar apenas a query SQL, sem nenhuma explicação adicional, texto introdutório ou conclusivo.
Use o esquema de banco de dados fornecido para construir a query.
Certifique-se de que a query seja sintaticamente correta e semanticamente coerente com a pergunta e o esquema.
Se a pergunta exigir agregações ou condições complexas, tente gerar a query mais precisa possível.
SEMPRE utilize o dialeto SQL para {dialect}.

Esquema do Banco de Dados:
{db_schema}

Instruções:
- A query SQL gerada deve ser para o banco de dados {dialect}.
- Não inclua blocos de código ou ```sql``` ao redor da query. Apenas a query SQL pura.
- Não inclua semicolons (;) no final da query.

Pergunta em Linguagem Natural: "{user_query}"

Query SQL:
"""
    return prompt