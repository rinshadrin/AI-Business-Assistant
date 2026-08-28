import json

from sqlalchemy import inspect

from backend.db import engine


# =========================================================
# DATABASE TABLES
# =========================================================

def get_real_database_tables():
    try:
        inspector = inspect(engine)
        return sorted(inspector.get_table_names())

    except Exception as e:
        print(f"[DATABASE TABLE ERROR] {e}")
        return []


# =========================================================
# DATABASE STRUCTURE QUESTIONS
# =========================================================

def handle_schema_question(question: str):

    q = question.lower().strip()

    # Ask LLM to understand schema-related questions.
    # No fixed list of user questions.

    try:
        from LLM.model import ask_llm

        prompt = f"""
You are an intent detector for a business database.

Determine whether this user question is asking about the
DATABASE STRUCTURE itself.

Examples of database-structure requests include:
- number of tables
- list of tables
- database structure
- what tables exist
- show database tables
- what columns exist
- database schema

USER QUESTION:
{question}

Return ONLY valid JSON:

{{
    "is_schema_question": true
}}

or

{{
    "is_schema_question": false
}}
"""

        response = ask_llm(prompt)

        response = response.strip()

        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

        result = json.loads(response)

        if not result.get("is_schema_question", False):
            return None

    except Exception as e:
        print(f"[SCHEMA INTENT ERROR] {e}")

        # If LLM is unavailable, don't block normal questions.
        return None

    tables = get_real_database_tables()

    if not tables:
        return {
            "answer": "I couldn't find any tables in the connected database.",
            "sql": None,
            "data": [],
            "tables": [],
            "type": "database_overview",
            "intent": "database structure"
        }

    # Ask LLM what the user wants to know about the tables.
    try:

        from LLM.model import ask_llm

        table_text = "\n".join(
            f"{i}. {table}"
            for i, table in enumerate(tables, 1)
        )

        prompt = f"""
The database contains these tables:

{table_text}

USER QUESTION:
{question}

Answer the user's database-structure question using ONLY
the table list above.

Do not invent tables.

Return ONLY the answer.
"""

        answer = ask_llm(prompt).strip()

    except Exception:
        answer = (
            f"The database contains {len(tables)} tables:\n\n"
            + "\n".join(
                f"{i}. {table}"
                for i, table in enumerate(tables, 1)
            )
        )

    return {
        "answer": answer,
        "sql": None,
        "data": [],
        "tables": tables,
        "type": "database_overview",
        "intent": "database structure"
    }


# =========================================================
# SQL RESULT FORMATTER
# =========================================================

def format_sql_result(question, data):

    if not data:
        return "No matching business data was found."

    try:
        serialized_data = json.dumps(
            data,
            default=str,
            indent=2
        )

    except Exception:
        serialized_data = str(data)

    try:

        from LLM.model import ask_llm

        prompt = f"""
You are an AI Business Assistant.

Answer the user's question using ONLY the database result.

USER QUESTION:
{question}

DATABASE RESULT:
{serialized_data}

RULES:

1. Use only the database result.
2. Never invent information.
3. Never change numbers.
4. Preserve names and values.
5. Answer exactly what the user asked.
6. If multiple records exist, clearly list them.
7. Keep the answer concise and professional.
8. Do not mention SQL, RAG, routing or LLM.

Return ONLY the final answer.
"""

        answer = ask_llm(prompt)

        if answer:
            return answer.strip()

    except Exception as e:
        print(f"[SQL ANSWER ERROR] {e}")

    return format_raw_data(data)


# =========================================================
# RAW DATA FALLBACK
# =========================================================

def format_raw_data(data):

    if isinstance(data, list):

        lines = []

        for row in data:

            if isinstance(row, dict):

                values = []

                for key, value in row.items():
                    values.append(
                        f"{key}: {value}"
                    )

                lines.append(
                    " | ".join(values)
                )

            else:
                lines.append(str(row))

        return "\n".join(lines)

    if isinstance(data, dict):

        return "\n".join(
            f"{key}: {value}"
            for key, value in data.items()
        )

    return str(data)


# =========================================================
# RAG RESULT FORMATTER
# =========================================================

def format_rag_result(question, context):

    if not context:

        return (
            "The available business information "
            "is not sufficient to answer this question."
        )

    try:

        from LLM.model import ask_llm

        prompt = f"""
You are an AI Business Assistant.

Answer the user's question using ONLY the
provided business-document context.

USER QUESTION:
{question}

BUSINESS CONTEXT:
{context}

RULES:

1. Use only the supplied context.
2. Never invent information.
3. Never guess missing information.
4. Answer directly.
5. Keep the answer concise.
6. Do not mention RAG, embeddings or LLM.

Return ONLY the final answer.
"""

        answer = ask_llm(prompt)

        if answer:
            return answer.strip()

    except Exception as e:

        print(f"[RAG ANSWER ERROR] {e}")

    return str(context)


# =========================================================
# FIND TABLES FROM SQL
# =========================================================

def get_tables_from_sql(sql):

    if not sql:
        return []

    try:

        inspector = inspect(engine)

        real_tables = set(
            inspector.get_table_names()
        )

        found_tables = []

        for table in real_tables:

            pattern = rf"\b{table}\b"

            if __import__("re").search(
                pattern,
                sql,
                flags=__import__("re").IGNORECASE
            ):
                found_tables.append(table)

        return sorted(found_tables)

    except Exception as e:

        print(f"[SQL TABLE DETECTION ERROR] {e}")

        return []


# =========================================================
# MAIN AI FUNCTION
# =========================================================

def answer_business_question(question: str):

    question = str(question).strip()

    if not question:

        return {
            "answer": "Please enter a business question.",
            "sql": None,
            "data": [],
            "tables": [],
            "type": "unknown",
            "intent": ""
        }

    try:

        # =================================================
        # DATABASE STRUCTURE
        # =================================================

        schema_result = handle_schema_question(
            question
        )

        if schema_result is not None:

            return schema_result


        # =================================================
        # ROUTER
        # =================================================

        from backend.router import route_question

        route = route_question(question)

        if not isinstance(route, dict):

            return {
                "answer": (
                    "Unable to determine how to "
                    "answer the question."
                ),
                "sql": None,
                "data": [],
                "tables": [],
                "type": "error",
                "intent": ""
            }


        # =================================================
        # COMMON INFORMATION
        # =================================================

        route_type = route.get(
            "type",
            "unknown"
        )

        sql = route.get(
            "sql"
        )

        data = route.get(
            "data"
        )

        intent = route.get(
            "intent",
            ""
        )


        # =================================================
        # SQL
        # =================================================

        if route_type == "sql":

            answer = format_sql_result(
                question,
                data
            )

            tables = get_tables_from_sql(
                sql
            )

            return {
                "answer": answer,
                "sql": sql,
                "data": data or [],
                "tables": tables,
                "type": "sql",
                "intent": intent
            }


        # =================================================
        # DATABASE OVERVIEW
        # =================================================

        if route_type == "database_overview":

            return {
                "answer": route.get(
                    "answer",
                    "Database information retrieved."
                ),
                "sql": None,
                "data": [],
                "tables": get_real_database_tables(),
                "type": "database_overview",
                "intent": intent
            }


        # =================================================
        # RAG
        # =================================================

        if route_type == "rag":

            try:

                from rag.rag_pipeline import (
                    retrieve_context
                )

                context = retrieve_context(
                    question,
                    n_results=5
                )

                answer = format_rag_result(
                    question,
                    context
                )

            except Exception as e:

                print(
                    f"[RAG RETRIEVAL ERROR] {e}"
                )

                return {
                    "answer": (
                        "I was unable to retrieve "
                        "the relevant business information."
                    ),
                    "sql": None,
                    "data": [],
                    "tables": [],
                    "type": "error",
                    "intent": intent
                }

            return {
                "answer": answer,
                "sql": None,
                "data": [],
                "tables": [],
                "type": "rag",
                "intent": intent
            }


        # =================================================
        # ERROR
        # =================================================

        if route_type == "error":

            return {
                "answer": (
                    "I was unable to process "
                    "that business question."
                ),
                "sql": sql,
                "data": data or [],
                "tables": get_tables_from_sql(sql),
                "type": "error",
                "intent": intent
            }


        # =================================================
        # UNKNOWN
        # =================================================

        return {
            "answer": (
                "I could not determine how to "
                "answer that business question."
            ),
            "sql": sql,
            "data": data or [],
            "tables": get_tables_from_sql(sql),
            "type": "unknown",
            "intent": intent
        }


    except Exception as e:

        print(
            f"[AI SERVICE ERROR] {e}"
        )

        return {
            "answer": (
                "Unable to process the business "
                "question at the moment."
            ),
            "sql": None,
            "data": [],
            "tables": [],
            "type": "error",
            "intent": ""
        }
