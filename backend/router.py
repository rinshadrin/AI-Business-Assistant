import re
import json

from sqlalchemy import text, inspect


# ============================================================
# DATABASE
# ============================================================

try:
    from .db import SessionLocal
except ImportError:
    from db import SessionLocal


# ============================================================
# LLM
# ============================================================

try:
    from LLM.model import ask_llm
except ImportError:
    try:
        from ..LLM.model import ask_llm
    except ImportError:
        ask_llm = None


# ============================================================
# RAG
# ============================================================

try:
    from rag.rag_pipeline import retrieve_context
except Exception:
    try:
        from ..rag.rag_pipeline import retrieve_context
    except Exception:
        retrieve_context = None


# ============================================================
# GET DATABASE ENGINE
# ============================================================

def get_engine():

    session = SessionLocal()

    try:
        return session.get_bind()

    finally:
        session.close()


# ============================================================
# GET REAL DATABASE TABLES
# ============================================================

def get_real_database_tables():

    session = SessionLocal()

    try:

        engine = session.get_bind()

        inspector = inspect(engine)

        tables = inspector.get_table_names()

        return sorted(tables)

    except Exception as e:

        print("[TABLE ERROR]", e)

        return []

    finally:

        session.close()


# ============================================================
# GET REAL DATABASE SCHEMA
# ============================================================

def get_database_schema():

    session = SessionLocal()

    try:

        engine = session.get_bind()

        inspector = inspect(engine)

        tables = inspector.get_table_names()

        schema = []

        for table in tables:

            schema.append(
                f"TABLE: {table}"
            )

            columns = inspector.get_columns(table)

            for column in columns:

                schema.append(
                    f"  COLUMN: {column['name']}"
                )

            schema.append("")

        schema.append("RELATIONSHIPS:")

        for table in tables:

            try:

                foreign_keys = inspector.get_foreign_keys(
                    table
                )

                for fk in foreign_keys:

                    local_columns = (
                        fk.get("constrained_columns") or []
                    )

                    remote_table = fk.get(
                        "referred_table"
                    )

                    remote_columns = (
                        fk.get("referred_columns") or []
                    )

                    for local, remote in zip(
                        local_columns,
                        remote_columns
                    ):

                        schema.append(
                            f"{table}.{local} -> "
                            f"{remote_table}.{remote}"
                        )

            except Exception as e:

                print(
                    f"[FK WARNING] {table}: {e}"
                )

        return "\n".join(schema)

    except Exception as e:

        print(
            "[SCHEMA ERROR]",
            e
        )

        return ""

    finally:

        session.close()


# ============================================================
# DATABASE OVERVIEW
# ============================================================

def get_database_information():

    session = SessionLocal()

    try:

        engine = session.get_bind()

        inspector = inspect(engine)

        tables = inspector.get_table_names()

        result = []

        for table in tables:

            columns = [
                column["name"]
                for column in inspector.get_columns(table)
            ]

            try:

                count = session.execute(
                    text(
                        f"SELECT COUNT(*) "
                        f"FROM `{table}`"
                    )
                ).scalar()

            except Exception as e:

                print(
                    f"[COUNT ERROR] {table}: {e}"
                )

                count = "Unknown"

            result.append(
                {
                    "table": table,
                    "columns": columns,
                    "rows": count
                }
            )

        return result

    except Exception as e:

        print(
            "[DATABASE INFORMATION ERROR]",
            e
        )

        return []

    finally:

        session.close()


# ============================================================
# DATABASE OVERVIEW ANSWER
# ============================================================

def generate_database_overview():

    info = get_database_information()

    if not info:

        return (
            "I could not find any tables "
            "in the connected database."
        )

    answer = (
        f"The database contains "
        f"{len(info)} tables.\n\n"
    )

    for item in info:

        answer += (
            f"**{item['table']}** — "
            f"{item['rows']} records\n"
        )

    return answer


# ============================================================
# DIRECT DATABASE STRUCTURE QUESTION
# ============================================================

def handle_database_structure_question(question):

    q = question.lower().strip()

    # --------------------------------------------------------
    # HOW MANY TABLES
    # --------------------------------------------------------

    table_count_patterns = [

        r"\bhow many tables\b",

        r"\bhow many table\b",

        r"\bnumber of tables\b",

        r"\bnumber of table\b",

        r"\btotal tables\b",

        r"\btotal number of tables\b",

        r"\bhow much tables\b",

        r"\bhow many database tables\b",

    ]

    if any(
        re.search(
            pattern,
            q
        )
        for pattern in table_count_patterns
    ):

        tables = get_real_database_tables()

        count = len(tables)

        print(
            f"[DATABASE STRUCTURE] REAL TABLE COUNT = {count}"
        )

        return {
            "type": "database_overview",

            "data": {
                "table_count": count,
                "tables": tables
            },

            "sql": None,

            "intent": "count database tables",

            "answer":
                f"We have {count} tables in the database."
        }


    # --------------------------------------------------------
    # LIST TABLES
    # --------------------------------------------------------

    list_patterns = [

        r"\blist tables\b",

        r"\bshow tables\b",

        r"\blist all tables\b",

        r"\bshow all tables\b",

        r"\bwhat tables do we have\b",

        r"\bwhich tables do we have\b",

        r"\bwhat are the tables\b",

        r"\btable names\b",

        r"\bnames of tables\b",

        r"\blist database tables\b",

    ]

    if any(
        re.search(
            pattern,
            q
        )
        for pattern in list_patterns
    ):

        tables = get_real_database_tables()

        if not tables:

            return {
                "type": "database_overview",
                "data": None,
                "sql": None,
                "intent": "list database tables",
                "answer":
                    "I could not find any tables in the database."
            }

        answer = (
            f"The database contains "
            f"{len(tables)} tables:\n\n"
        )

        for index, table in enumerate(
            tables,
            start=1
        ):

            answer += (
                f"{index}. {table}\n"
            )

        return {
            "type": "database_overview",

            "data": {
                "table_count": len(tables),
                "tables": tables
            },

            "sql": None,

            "intent": "list database tables",

            "answer": answer
        }


    # --------------------------------------------------------
    # DATABASE STRUCTURE / SCHEMA
    # --------------------------------------------------------

    structure_patterns = [

        "database structure",

        "database schema",

        "show schema",

        "show database schema",

        "show database structure",

        "what is the database structure",

        "what is the database schema",

        "tables and columns",

        "show tables and columns",

        "list tables and columns",

    ]

    if any(
        phrase in q
        for phrase in structure_patterns
    ):

        info = get_database_information()

        if not info:

            return {
                "type": "database_overview",
                "data": None,
                "sql": None,
                "intent": "database structure",
                "answer":
                    "I could not read the database structure."
            }

        answer = (
            f"## Database Structure\n\n"
            f"The database contains "
            f"**{len(info)} tables**.\n\n"
        )

        for item in info:

            answer += (
                f"### {item['table']}\n"
            )

            answer += (
                f"Records: **{item['rows']}**\n\n"
            )

            answer += "Columns:\n"

            for column in item["columns"]:

                answer += (
                    f"- `{column}`\n"
                )

            answer += "\n"

        return {
            "type": "database_overview",

            "data": info,

            "sql": None,

            "intent": "database structure",

            "answer": answer
        }


    return None


# ============================================================
# EXTRACT JSON
# ============================================================

def extract_json(response):

    if not response:
        return None

    raw = str(response).strip()

    raw = re.sub(
        r"```json\s*",
        "",
        raw,
        flags=re.IGNORECASE
    )

    raw = re.sub(
        r"```",
        "",
        raw
    ).strip()

    # First try complete response
    try:

        data = json.loads(raw)

        if isinstance(data, dict):
            return data

    except Exception:
        pass

    # Try extracting JSON object
    match = re.search(
        r"\{.*\}",
        raw,
        flags=re.DOTALL
    )

    if match:

        try:

            data = json.loads(
                match.group(0)
            )

            if isinstance(data, dict):
                return data

        except Exception:
            pass

    return None


# ============================================================
# UNDERSTAND QUESTION
# ============================================================

def understand_question(question):

    # IMPORTANT:
    # Database structure questions are already handled
    # before this function is called.

    schema = get_database_schema()

    prompt = f"""
You are the intelligent router of an AI Business Assistant.

Understand the user's question by MEANING.

Choose exactly ONE route:

SQL
- live information from database
- customers
- products
- orders
- sales
- revenue
- costs
- inventory
- suppliers
- employees
- payments
- profit
- loss
- counts of business records
- totals
- averages
- rankings
- comparisons

RAG
- company documents
- policies
- manuals
- procedures
- guidelines
- business documents
- unstructured information

DATABASE_OVERVIEW
- number of database tables
- names of database tables
- database schema
- database structure
- table columns
- relationships between tables

IMPORTANT:

Questions such as:

"how many tables do we have?"
"how many tables are there?"
"list the tables"
"show database structure"

must be DATABASE_OVERVIEW.

Do NOT treat those questions as normal SQL business questions.

USER QUESTION:
{question}

DATABASE SCHEMA:
{schema}

Return ONLY valid JSON:

{{
    "route": "SQL",
    "intent": "what the user wants",
    "needs_database": true,
    "needs_documents": false
}}
"""

    if ask_llm is None:

        return {
            "route": "SQL",
            "intent": "business database question",
            "needs_database": True,
            "needs_documents": False
        }

    try:

        response = ask_llm(prompt)

        print("\n[LLM ROUTER]")
        print(response)

        result = extract_json(response)

        if not result:

            raise ValueError(
                "Invalid JSON from LLM"
            )

        route = str(
            result.get(
                "route",
                "SQL"
            )
        ).upper().strip()

        if route not in {
            "SQL",
            "RAG",
            "DATABASE_OVERVIEW"
        }:

            route = "SQL"

        return {
            "route": route,

            "intent": str(
                result.get(
                    "intent",
                    "business question"
                )
            ),

            "needs_database": bool(
                result.get(
                    "needs_database",
                    route == "SQL"
                )
            ),

            "needs_documents": bool(
                result.get(
                    "needs_documents",
                    route == "RAG"
                )
            )
        }

    except Exception as e:

        print(
            "[ROUTER ERROR]:",
            e
        )

        return {
            "route": "SQL",
            "intent": "business database question",
            "needs_database": True,
            "needs_documents": False
        }


# ============================================================
# CLEAN SQL
# ============================================================

def clean_sql(raw_sql):

    if not raw_sql:
        return ""

    sql = str(raw_sql).strip()

    sql = re.sub(
        r"```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```",
        "",
        sql
    ).strip()

    match = re.search(
        r"\bSELECT\b",
        sql,
        flags=re.IGNORECASE
    )

    if not match:
        return ""

    sql = sql[match.start():]

    if ";" in sql:
        sql = sql.split(";")[0]

    return sql.strip()


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(question, intent=""):

    schema = get_database_schema()

    prompt = f"""
You are an expert Text-to-SQL engine.

Convert the user's natural-language business question
into ONE correct MySQL SELECT query.

USER QUESTION:
{question}

USER INTENT:
{intent}

REAL DATABASE SCHEMA:
{schema}

IMPORTANT RULES:

1. Use ONLY tables shown in the schema.
2. Use ONLY columns shown in the schema.
3. Use ONLY real foreign-key relationships.
4. NEVER invent tables.
5. NEVER invent columns.
6. NEVER invent aliases.
7. Every alias must be defined by FROM or JOIN.
8. The query MUST contain FROM.
9. Only SELECT is allowed.

For "who" questions:
return names/entities, not COUNT.

For "which" questions:
return requested entities.

For "how many":
use COUNT.

For total:
use SUM where appropriate.

For average:
use AVG.

For highest/top/most:
use ORDER BY DESC.

For lowest/least:
use ORDER BY ASC.

For rankings:
return the ranked records.

For profit/loss:
use actual revenue and cost information
available in the schema.

Do NOT invent profit columns.

Do NOT invent expense columns.

Do NOT multiply an already-complete order total
by order-item quantity.

Never use:

INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
TRUNCATE
REPLACE
GRANT
REVOKE

Return ONLY the SQL query.
No markdown.
No explanation.
"""

    if ask_llm is None:
        return ""

    try:

        response = ask_llm(prompt)

        sql = clean_sql(response)

        print("\n[GENERATED SQL]")
        print(sql)

        return sql

    except Exception as e:

        print(
            "[SQL GENERATION ERROR]:",
            e
        )

        return ""


# ============================================================
# VALIDATE SQL
# ============================================================

def validate_sql(sql):

    if not sql:

        return False, "Empty SQL query."

    upper = sql.upper().strip()

    if not upper.startswith("SELECT"):

        return (
            False,
            "Only SELECT queries are allowed."
        )

    forbidden = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "REPLACE",
        "GRANT",
        "REVOKE"
    ]

    for word in forbidden:

        if re.search(
            rf"\b{word}\b",
            upper
        ):

            return (
                False,
                f"Unsafe SQL keyword: {word}"
            )

    if not re.search(
        r"\bFROM\b",
        upper
    ):

        return (
            False,
            "SELECT query must contain FROM."
        )

    return True, None


# ============================================================
# VALIDATE SQL AGAINST REAL SCHEMA
# ============================================================

def validate_sql_against_schema(sql):

    session = SessionLocal()

    try:

        engine = session.get_bind()

        inspector = inspect(engine)

        tables = inspector.get_table_names()

        table_columns = {}

        for table in tables:

            table_columns[table] = {
                c["name"]
                for c in inspector.get_columns(table)
            }

        # ----------------------------------------------------
        # FIND TABLES AND ALIASES
        # ----------------------------------------------------

        aliases = {}

        pattern = re.compile(
            r"\b(?:FROM|JOIN)\s+"
            r"[`\"]?([A-Za-z_][A-Za-z0-9_]*)[`\"]?"
            r"(?:\s+(?:AS\s+)?"
            r"([A-Za-z_][A-Za-z0-9_]*))?",
            flags=re.IGNORECASE
        )

        for match in pattern.finditer(sql):

            table = match.group(1)

            alias = match.group(2)

            if table not in table_columns:

                return (
                    False,
                    f"Table '{table}' does not exist."
                )

            aliases[table] = table

            if alias:

                aliases[alias] = table

        if not aliases:

            return (
                False,
                "No valid database table found."
            )

        # ----------------------------------------------------
        # CHECK ALIAS.COLUMNS
        # ----------------------------------------------------

        column_pattern = re.compile(
            r"\b([A-Za-z_][A-Za-z0-9_]*)"
            r"\.([A-Za-z_][A-Za-z0-9_]*)\b"
        )

        for match in column_pattern.finditer(sql):

            alias = match.group(1)

            column = match.group(2)

            if alias not in aliases:
                continue

            table = aliases[alias]

            if column not in table_columns[table]:

                return (
                    False,
                    f"Column '{column}' does not exist "
                    f"in table '{table}'."
                )

        return True, None

    except Exception as e:

        print(
            "[SCHEMA CHECK WARNING]:",
            e
        )

        return True, None

    finally:

        session.close()


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    valid, error = validate_sql(sql)

    if not valid:
        raise ValueError(error)

    valid, error = validate_sql_against_schema(sql)

    if not valid:
        raise ValueError(error)

    session = SessionLocal()

    try:

        print("\n[DATABASE SQL]")
        print(sql)

        result = session.execute(
            text(sql)
        )

        rows = result.mappings().all()

        data = [
            dict(row)
            for row in rows
        ]

        print(
            "[DATABASE] Rows:",
            len(data)
        )

        return data

    finally:

        session.close()


# ============================================================
# REPAIR SQL
# ============================================================

def repair_sql(
    question,
    intent,
    bad_sql,
    error_message
):

    schema = get_database_schema()

    prompt = f"""
You are an expert SQL debugger.

Repair the SQL query so it correctly answers
the user's question.

USER QUESTION:
{question}

INTENT:
{intent}

FAILED SQL:
{bad_sql}

DATABASE ERROR:
{error_message}

REAL DATABASE SCHEMA:
{schema}

RULES:

Use ONLY real tables.

Use ONLY real columns.

Use ONLY real foreign keys.

Every alias must be defined by FROM or JOIN.

Do not invent aliases.

Do not invent tables.

Do not invent columns.

The query MUST contain FROM.

Preserve the user's meaning.

Only SELECT is allowed.

Return ONLY the corrected SQL.
"""

    if ask_llm is None:
        return ""

    try:

        response = ask_llm(prompt)

        sql = clean_sql(response)

        print("\n[REPAIRED SQL]")
        print(sql)

        return sql

    except Exception as e:

        print(
            "[REPAIR ERROR]:",
            e
        )

        return ""


# ============================================================
# SQL RETRY
# ============================================================

def execute_sql_with_retry(
    question,
    intent,
    sql,
    max_retries=3
):

    current_sql = sql

    last_error = None

    for attempt in range(
        max_retries + 1
    ):

        print(
            f"\n[SQL ATTEMPT] {attempt + 1}"
        )

        try:

            data = execute_sql(
                current_sql
            )

            return {
                "success": True,
                "data": data,
                "sql": current_sql,
                "attempt": attempt + 1
            }

        except Exception as e:

            last_error = str(e)

            print(
                "[SQL ERROR]:",
                last_error
            )

            if attempt >= max_retries:
                break

            repaired = repair_sql(
                question,
                intent,
                current_sql,
                last_error
            )

            if not repaired:
                break

            current_sql = repaired

    return {
        "success": False,
        "data": None,
        "sql": current_sql,
        "error": last_error
    }


# ============================================================
# FORMAT BUSINESS ANSWER
# ============================================================

def format_business_answer(
    question,
    intent,
    data
):

    if not data:

        return (
            "No matching records were "
            "found in the database."
        )

    result_text = "\n".join(
        f"Record {i}: {row}"
        for i, row in enumerate(
            data,
            1
        )
    )

    prompt = f"""
Answer the user's question using ONLY
the database result.

USER QUESTION:
{question}

INTENT:
{intent}

DATABASE RESULT:
{result_text}

Rules:

Answer the actual question.

Do not invent information.

Do not change database values.

If the user asks WHO,
provide the name.

If the user asks WHICH,
provide the entities.

If multiple rows exist,
explain them clearly.

If it is a count,
state the count.

If it is revenue/cost/profit/loss,
explain the returned values naturally.

Do not show SQL.

Do not show Python dictionaries.

Do not mention internal routing.

Return ONLY the answer.
"""

    if ask_llm is None:

        return "\n".join(
            " | ".join(
                f"{k}: {v}"
                for k, v in row.items()
            )
            for row in data
        )

    try:

        answer = ask_llm(
            prompt
        ).strip()

        if answer:
            return answer

    except Exception as e:

        print(
            "[ANSWER ERROR]:",
            e
        )

    return "\n".join(
        " | ".join(
            f"{k}: {v}"
            for k, v in row.items()
        )
        for row in data
    )


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve_rag_context(question):

    if retrieve_context is None:

        raise RuntimeError(
            "RAG pipeline is not available."
        )

    try:

        return retrieve_context(
            question,
            n_results=5
        )

    except TypeError:

        return retrieve_context(
            question
        )


# ============================================================
# FORMAT RAG ANSWER
# ============================================================

def format_rag_answer(
    question,
    intent,
    context
):

    if not context:

        return (
            "I could not find relevant "
            "information in the documents."
        )

    prompt = f"""
Answer the user's question using ONLY
the retrieved document context.

USER QUESTION:
{question}

INTENT:
{intent}

DOCUMENT CONTEXT:
{context}

Do not invent information.

If the context does not contain
the answer, say so.

Return ONLY the answer.
"""

    if ask_llm is None:
        return str(context)

    try:

        return ask_llm(
            prompt
        ).strip()

    except Exception:

        return str(context)


# ============================================================
# MAIN ROUTER
# ============================================================

def route_question(question):

    question = str(
        question
    ).strip()

    print("\n================================")
    print("[QUESTION]", question)
    print("================================")

    if not question:

        return {
            "type": "unknown",
            "data": None,
            "sql": None,
            "answer": "Please enter a question."
        }

    # ========================================================
    # VERY IMPORTANT
    # DATABASE STRUCTURE QUESTIONS ARE HANDLED FIRST
    #
    # LLM IS NOT USED FOR THESE QUESTIONS.
    # ========================================================

    structure_result = (
        handle_database_structure_question(
            question
        )
    )

    if structure_result is not None:

        print(
            "[ROUTE] DATABASE_OVERVIEW"
        )

        print(
            "[STRUCTURE RESULT]",
            structure_result
        )

        return structure_result


    # ========================================================
    # UNDERSTAND NORMAL QUESTION
    # ========================================================

    understanding = understand_question(
        question
    )

    route = understanding["route"]

    intent = understanding["intent"]

    print(
        "[ROUTE]",
        route
    )

    print(
        "[INTENT]",
        intent
    )


    # ========================================================
    # DATABASE OVERVIEW
    # ========================================================

    if route == "DATABASE_OVERVIEW":

        try:

            answer = generate_database_overview()

            return {
                "type": "database_overview",

                "data": get_database_information(),

                "sql": None,

                "intent": intent,

                "answer": answer
            }

        except Exception as e:

            return {
                "type": "error",

                "data": None,

                "sql": None,

                "intent": intent,

                "message": str(e),

                "answer":
                    "I could not read the database."
            }


    # ========================================================
    # SQL
    # ========================================================

    if route == "SQL":

        sql = generate_sql(
            question,
            intent
        )

        if not sql:

            return {
                "type": "error",

                "data": None,

                "sql": None,

                "intent": intent,

                "answer":
                    "I could not generate "
                    "a database query."
            }

        result = execute_sql_with_retry(
            question,
            intent,
            sql
        )

        if not result["success"]:

            return {
                "type": "error",

                "data": None,

                "sql": result["sql"],

                "intent": intent,

                "message": result["error"],

                "answer":
                    "I could not execute "
                    "the database query."
            }

        data = result["data"]

        answer = format_business_answer(
            question,
            intent,
            data
        )

        return {
            "type": "sql",

            "data": data,

            "sql": result["sql"],

            "attempt": result["attempt"],

            "intent": intent,

            "answer": answer
        }


    # ========================================================
    # RAG
    # ========================================================

    if route == "RAG":

        try:

            context = retrieve_rag_context(
                question
            )

            answer = format_rag_answer(
                question,
                intent,
                context
            )

            return {
                "type": "rag",

                "data": {
                    "question": question,
                    "context": context
                },

                "sql": None,

                "intent": intent,

                "answer": answer
            }

        except Exception as e:

            return {
                "type": "error",

                "data": None,

                "sql": None,

                "intent": intent,

                "message": str(e),

                "answer":
                    "I could not retrieve "
                    "the business documents."
            }


    # ========================================================
    # FALLBACK
    # ========================================================

    return {
        "type": "unknown",

        "data": None,

        "sql": None,

        "intent": intent,

        "answer":
            "I could not determine "
            "how to answer that question."
    }


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "AI BUSINESS ASSISTANT - ROUTER TEST"
    )

    while True:

        question = input(
            "\nAsk a question "
            "(type exit to stop): "
        ).strip()

        if question.lower() == "exit":
            break

        result = route_question(
            question
        )

        print(
            "\n========== ANSWER =========="
        )

        print(
            result.get(
                "answer",
                "No answer."
            )
        )

        print(
            "\n========== SQL =========="
        )

        print(
            result.get(
                "sql",
                "None"
            )
        )

        print(
            "\n========== TYPE =========="
        )

        print(
            result.get(
                "type",
                "unknown"
            )
        )

        print(
            "\n========== INTENT =========="
        )

        print(
            result.get(
                "intent",
                ""
            )
        )
