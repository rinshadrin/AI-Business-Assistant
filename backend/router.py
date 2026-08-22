import re

from sqlalchemy import text, inspect


# ============================================================
# IMPORT DATABASE
# ============================================================

try:
    from .db import SessionLocal
except ImportError:
    from db import SessionLocal


# ============================================================
# IMPORT LLM
# ============================================================

try:
    from LLM.model import ask_llm
except ImportError:
    try:
        from ..LLM.model import ask_llm
    except ImportError:
        ask_llm = None


# ============================================================
# IMPORT RAG
# ============================================================

try:
    from rag.rag_pipeline import retrieve_context
except Exception:
    try:
        from ..rag.rag_pipeline import retrieve_context
    except Exception:
        retrieve_context = None


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_engine():
    session = SessionLocal()

    try:
        engine = session.get_bind()

        print("[DATABASE] Connected to:", engine.url)

        return engine

    except Exception as e:
        session.close()

        print("[DATABASE CONNECTION ERROR]", e)

        raise


# ============================================================
# READ ACTUAL DATABASE SCHEMA + RELATIONSHIPS
# ============================================================

def get_database_schema():

    session = SessionLocal()

    try:
        engine = session.get_bind()
        inspector = inspect(engine)

        table_names = inspector.get_table_names()

        print("[SCHEMA] Tables found:", table_names)

        if not table_names:
            print("[SCHEMA] WARNING: No tables found!")
            return ""

        schema_parts = []
        relationships = []

        for table_name in table_names:

            print(f"[SCHEMA] Reading table: {table_name}")

            columns_info = inspector.get_columns(table_name)

            # ------------------------------------------------
            # PRIMARY KEYS
            # ------------------------------------------------

            try:
                pk_info = inspector.get_pk_constraint(table_name)

                pk_columns = pk_info.get(
                    "constrained_columns",
                    []
                )

            except Exception:
                pk_columns = []

            column_lines = []

            for column in columns_info:

                column_name = column["name"]
                column_type = str(column["type"])

                primary_key = ""

                if column_name in pk_columns:
                    primary_key = " PRIMARY KEY"

                column_lines.append(
                    f"- {column_name} {column_type}{primary_key}"
                )

            schema_parts.append(
                f"TABLE: {table_name}\n"
                + "\n".join(column_lines)
            )

            # ------------------------------------------------
            # FOREIGN KEYS
            # ------------------------------------------------

            try:
                foreign_keys = inspector.get_foreign_keys(
                    table_name
                )

                for fk in foreign_keys:

                    constrained_columns = fk.get(
                        "constrained_columns",
                        []
                    )

                    referred_table = fk.get(
                        "referred_table"
                    )

                    referred_columns = fk.get(
                        "referred_columns",
                        []
                    )

                    if (
                        referred_table
                        and constrained_columns
                        and referred_columns
                    ):

                        for local_col, remote_col in zip(
                            constrained_columns,
                            referred_columns
                        ):

                            relationships.append(
                                f"{table_name}.{local_col} "
                                f"-> "
                                f"{referred_table}.{remote_col}"
                            )

            except Exception as e:

                print(
                    f"[SCHEMA] Foreign key error "
                    f"for {table_name}: {e}"
                )

        schema = "\n\n".join(schema_parts)

        # ----------------------------------------------------
        # ADD RELATIONSHIPS
        # ----------------------------------------------------

        schema += "\n\nRELATIONSHIPS:\n"

        if relationships:

            for relationship in relationships:
                schema += f"- {relationship}\n"

        else:

            schema += (
                "- No foreign-key relationships were "
                "reported by the database.\n"
            )

        print("[SCHEMA] Successfully loaded.")

        print("\n[SCHEMA WITH RELATIONSHIPS]")
        print(schema)

        return schema

    except Exception as e:

        print("[SCHEMA ERROR]:", e)

        return ""

    finally:

        session.close()


# ============================================================
# READ ACTUAL DATABASE INFORMATION
# ============================================================

def get_database_information():

    session = SessionLocal()

    try:

        engine = session.get_bind()

        print("[DATABASE] Connected to:", engine.url)

        inspector = inspect(engine)

        table_names = inspector.get_table_names()

        print("[DATABASE] Tables found:", table_names)

        if not table_names:

            print(
                "[DATABASE] WARNING: Database has no tables."
            )

            return []

        information = []

        for table_name in table_names:

            print(
                f"[DATABASE] Reading table: {table_name}"
            )

            columns_info = inspector.get_columns(
                table_name
            )

            columns = [
                column["name"]
                for column in columns_info
            ]

            try:

                count = session.execute(
                    text(
                        f'SELECT COUNT(*) '
                        f'FROM "{table_name}"'
                    )
                ).scalar()

            except Exception as e:

                print(
                    f"[DATABASE] Count error "
                    f"for {table_name}: {e}"
                )

                count = "Unknown"

            information.append(
                {
                    "table": table_name,
                    "columns": columns,
                    "rows": count
                }
            )

        print(
            "[DATABASE] Successfully read",
            len(information),
            "tables."
        )

        return information

    except Exception as e:

        print("[DATABASE ERROR]:", e)

        return []

    finally:

        session.close()


# ============================================================
# DATABASE OVERVIEW DETECTOR
# ============================================================

def is_database_overview_question(question):

    q = question.lower().strip()

    q = re.sub(
        r"[?.!,]",
        "",
        q
    )

    patterns = [

        "explain the data in the database",
        "explain data in the database",
        "explain the database",
        "explain our database",
        "describe the database",
        "describe our database",
        "database overview",
        "overview of the database",
        "overview of our database",
        "what data is in the database",
        "what data is stored in the database",
        "what information is stored in the database",
        "what information is in the database",
        "what information do we have in the database",
        "what data do we have in the database",
        "what tables do we have",
        "what tables are in the database",
        "show me the database structure",
        "show the database structure",
        "explain the database structure",
        "what kind of data do we have",
        "what kind of information do we have",
        "tell me about the database",
        "tell me about our database",
        "give me an overview of the database",
        "give me an overview of our database"
    ]

    for pattern in patterns:

        if pattern in q:
            return True

    if "explain" in q and "database" in q:
        return True

    if "describe" in q and "database" in q:
        return True

    if "overview" in q and "database" in q:
        return True

    if "tables" in q and "database" in q:
        return True

    if "data" in q and "database" in q:
        return True

    return False


# ============================================================
# DATABASE OVERVIEW ANSWER
# ============================================================

def generate_database_overview(question):

    print("[OVERVIEW] Reading database...")

    database_info = get_database_information()

    print(
        "[OVERVIEW] Database information loaded."
    )

    if not database_info:

        return (
            "I could not find any tables "
            "in the connected database."
        )

    answer = ""

    answer += "## 🗄️ Database Overview\n\n"

    answer += (
        "Your business database contains "
        f"**{len(database_info)} tables**.\n\n"
    )

    for item in database_info:

        table_name = item["table"]
        columns = item["columns"]
        rows = item["rows"]

        answer += (
            f"### 📋 {table_name}\n\n"
        )

        answer += (
            f"**Records:** {rows}\n\n"
        )

        answer += "**Columns:**\n"

        for column in columns:

            answer += f"- `{column}`\n"

        answer += "\n"

    answer += "---\n\n"

    answer += (
        "### 💼 Business information available\n\n"
    )

    answer += (
        "This database can be used to answer "
        "questions about customers, products, "
        "orders, inventory, suppliers, payments, "
        "employees, sales, revenue and business "
        "performance.\n"
    )

    return answer


# ============================================================
# QUESTION CLASSIFICATION
# ============================================================

def classify_question(question):

    if is_database_overview_question(question):
        return "database_overview"

    schema = get_database_schema()

    prompt = f"""
You are the router of an AI Business Assistant.

Classify the user's question into exactly ONE
of these categories:

SQL
RAG

================================================
SQL
================================================

Use SQL when the question asks about actual
business data stored in the database.

Examples:

How many customers do we have?
SQL

Which products have low stock?
SQL

Which products need restocking?
SQL

Show the top 5 expensive products.
SQL

Who are our top customers?
SQL

What is our total revenue?
SQL

Are we making a profit or loss?
SQL

How many orders have been placed?
SQL

Which customer ordered the least?
SQL

Which customer spent the most?
SQL

What products did the customer who spent the
most money buy?
SQL

================================================
RAG
================================================

Use RAG only for company documents, policies,
procedures, manuals and rules.

Examples:

What is our refund policy?
RAG

What is the leave policy?
RAG

How can employees apply for leave?
RAG

================================================
DATABASE QUESTIONS
================================================

Questions about tables, columns, records,
customers, products, orders, suppliers,
employees, payments, inventory, revenue,
sales or business performance are SQL.

================================================
DATABASE SCHEMA
================================================

{schema}

================================================
USER QUESTION
================================================

{question}

Return ONLY:

SQL

or

RAG
"""

    try:

        if ask_llm is None:
            return "sql"

        response = ask_llm(prompt)

        result = response.strip().upper()

        print(
            "[CLASSIFIER RESULT]:",
            result
        )

        # Check SQL first because the word SQL
        # is the expected database route.

        if re.search(
            r"\bSQL\b",
            result
        ):
            return "sql"

        if re.search(
            r"\bRAG\b",
            result
        ):
            return "rag"

    except Exception as e:

        print(
            "[CLASSIFIER ERROR]:",
            e
        )

    return "sql"


# ============================================================
# CLEAN SQL
# ============================================================

def clean_sql(raw_sql):

    if not raw_sql:
        return ""

    sql = raw_sql.strip()

    # Remove markdown code fences
    sql = re.sub(
        r"```sql",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```",
        "",
        sql
    )

    # Find SELECT
    match = re.search(
        r"\bSELECT\b",
        sql,
        flags=re.IGNORECASE
    )

    if not match:
        return ""

    sql = sql[match.start():]

    # Remove anything after first semicolon
    semicolon = sql.find(";")

    if semicolon != -1:
        sql = sql[:semicolon]

    return sql.strip()


# ============================================================
# SQL VALIDATION
# ============================================================

def validate_sql(sql):

    if not sql:

        return (
            False,
            "SQL query is empty."
        )

    sql_upper = sql.upper().strip()

    if not sql_upper.startswith("SELECT"):

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

    for keyword in forbidden:

        if re.search(
            rf"\b{keyword}\b",
            sql_upper
        ):

            return (
                False,
                f"Unsafe SQL keyword: {keyword}"
            )

    return True, None


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(question):

    schema = get_database_schema()

    if not schema:

        print(
            "[SQL] No database schema found."
        )

        return ""

    prompt = f"""
You are an expert SQL generator for an ERP
Business Assistant.

Your job is to generate ONE correct SQL SELECT
query that answers the user's question.

================================================
DATABASE SCHEMA
================================================

{schema}

================================================
CRITICAL DATABASE RELATIONSHIP RULE
================================================

You MUST follow the relationships listed in
the schema.

NEVER assume that a column belongs to a table.

For example:

If orders contains customer_id but does NOT
contain customer_name, you MUST JOIN customers.

Correct:

customers AS c
JOIN orders AS o
ON c.customer_id = o.customer_id

Incorrect:

orders AS o
SELECT o.customer_name

For product information, use products.

For order quantities, use order_items.

For customer information, use customers.

For order information, use orders.

For relationships, follow the actual foreign
keys listed in the schema.

================================================
COMMON ERP RELATIONSHIPS
================================================

When these tables exist, the normal relationship
is generally:

customers.customer_id
    ->
orders.customer_id

orders.order_id
    ->
order_items.order_id

products.product_id
    ->
order_items.product_id

BUT ALWAYS CHECK THE ACTUAL RELATIONSHIPS
LISTED IN THE DATABASE SCHEMA ABOVE.

================================================
USER QUESTION
================================================

{question}

================================================
SQL RULES
================================================

1. Return ONLY SQL.

2. SELECT queries only.

3. Never invent tables.

4. Never invent columns.

5. Use ONLY columns present in the schema.

6. Use table aliases carefully.

7. Never select a column from an alias unless
   that column actually exists in that alias's
   table.

8. Use correct JOIN conditions.

9. Follow foreign-key relationships.

10. If customer_name is needed, JOIN the
    customers table if necessary.

11. If product_name is needed, JOIN the
    products table if necessary.

12. If order quantity is needed, use
    order_items.quantity when available.

13. If the user asks "how many", use COUNT(*)
    or an appropriate aggregate.

14. If the user asks "which", "who", "show",
    "list", "give me" or "what are", return
    actual records.

15. NEVER convert a list question into COUNT(*).

16. TOP N must return N records.

17. Cheapest means price ASC.

18. Most expensive means price DESC.

19. Highest means DESC.

20. Lowest means ASC.

21. Low stock means:

    stock_quantity <= reorder_level

22. For low-stock questions return useful
    product information including:
    product name, stock quantity and
    reorder level when those columns exist.

23. For expensive/cheap product questions,
    return product name and price.

24. For customer spending questions, calculate
    spending from the correct database fields.

25. If orders.total_amount represents the
    complete order value, use orders.total_amount.

26. Do NOT multiply orders.total_amount by
    order_items.quantity.

27. For best-selling products, use
    order_items.quantity when available.

28. Use GROUP BY when aggregation is required.

29. Use ORDER BY for rankings.

30. Use LIMIT for TOP N.

31. Preserve user filters.

32. Preserve dates.

33. If a question asks for a customer's products,
    JOIN customers -> orders -> order_items
    -> products when those relationships exist.

34. If a question asks for the customer who
    ordered the least, determine the customer
    using order counts and then retrieve that
    customer's actual information.

35. If a question asks which customer spent the
    most, calculate spending per customer and
    rank it correctly.

36. If a question asks for customers who never
    ordered, use an appropriate LEFT JOIN or
    NOT EXISTS query.

37. If a question asks for products never ordered,
    use an appropriate LEFT JOIN or NOT EXISTS
    query.

38. Do not use INSERT.

39. Do not use UPDATE.

40. Do not use DELETE.

41. Do not use DROP.

42. Do not use ALTER.

43. Do not use CREATE.

44. Do not add explanations.

45. Do not use markdown.

Return ONLY the SQL query.
"""

    try:

        print(
            "[SQL] Asking LLM to generate SQL..."
        )

        if ask_llm is None:

            print(
                "[SQL] LLM is not available."
            )

            return ""

        raw_sql = ask_llm(prompt)

    except Exception as e:

        print(
            "[SQL GENERATION ERROR]:",
            e
        )

        return ""

    sql = clean_sql(raw_sql)

    print("\n[GENERATED SQL]")
    print(sql)

    return sql


# ============================================================
# EXTRA SCHEMA-AWARE SQL VALIDATION
# ============================================================

def validate_sql_against_schema(sql):

    """
    Basic validation to catch obvious cases where
    the generated SQL references a table alias and
    column that does not exist.

    Database execution remains the final authority.
    """

    if not sql:
        return True, None

    session = SessionLocal()

    try:

        engine = session.get_bind()
        inspector = inspect(engine)

        tables = inspector.get_table_names()

        table_columns = {}

        for table in tables:

            table_columns[table] = {
                column["name"]
                for column in inspector.get_columns(table)
            }

        # ----------------------------------------------------
        # Find aliases from FROM/JOIN
        # ----------------------------------------------------

        alias_pattern = re.compile(
            r"""
            \b
            (?:FROM|JOIN)
            \s+
            [`"]?([A-Za-z_][A-Za-z0-9_]*)[`"]?
            \s+
            (?:AS\s+)?
            ([A-Za-z_][A-Za-z0-9_]*)
            """,
            re.IGNORECASE | re.VERBOSE
        )

        aliases = {}

        for match in alias_pattern.finditer(sql):

            table_name = match.group(1)
            alias = match.group(2)

            if table_name in table_columns:

                aliases[alias] = table_name

        # ----------------------------------------------------
        # Find alias.column references
        # ----------------------------------------------------

        column_pattern = re.compile(
            r"\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\b"
        )

        for match in column_pattern.finditer(sql):

            alias = match.group(1)
            column = match.group(2)

            if alias in aliases:

                table_name = aliases[alias]

                if column not in table_columns[table_name]:

                    return (
                        False,
                        f"Column '{column}' does not exist "
                        f"in table '{table_name}' "
                        f"(alias '{alias}')."
                    )

        return True, None

    except Exception as e:

        print(
            "[SCHEMA VALIDATION WARNING]:",
            e
        )

        # Do not block a valid query because the
        # optional validator itself failed.
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

    schema_valid, schema_error = (
        validate_sql_against_schema(sql)
    )

    if not schema_valid:

        raise ValueError(
            f"Schema validation failed: {schema_error}"
        )

    session = SessionLocal()

    try:

        print(
            "[DATABASE] Executing SQL..."
        )

        result = session.execute(
            text(sql)
        )

        rows = result.mappings().all()

        data = [
            dict(row)
            for row in rows
        ]

        print(
            "[DATABASE] Rows returned:",
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
    bad_sql,
    error_message
):

    schema = get_database_schema()

    prompt = f"""
You are an expert SQL debugger for an ERP
database.

The generated SQL failed.

Fix the SQL while preserving the user's
original question.

================================================
DATABASE SCHEMA
================================================

{schema}

================================================
USER QUESTION
================================================

{question}

================================================
FAILED SQL
================================================

{bad_sql}

================================================
DATABASE ERROR
================================================

{error_message}

================================================
CRITICAL
================================================

The database schema above is authoritative.

DO NOT invent columns.

If a column belongs to another table, JOIN
that table.

For example, if:

customers.customer_id
    ->
orders.customer_id

then customer_name must come from customers,
not orders.

If product_name is needed, use products.

If quantity is needed, use order_items.

Follow the foreign-key relationships.

================================================
RULES
================================================

1. Return ONLY one SELECT query.

2. Use only existing tables.

3. Use only existing columns.

4. Fix invalid columns.

5. Fix incorrect aliases.

6. Fix JOIN problems.

7. Preserve the original question.

8. Preserve filters.

9. Preserve aggregation.

10. Preserve ORDER BY.

11. Preserve LIMIT.

12. If the user asks for records,
    return records.

13. Do not convert list questions
    into COUNT(*).

14. Use correct foreign-key relationships.

15. SELECT only.

16. No explanation.

Return ONLY corrected SQL.
"""

    try:

        print(
            "[SQL REPAIR] Asking LLM..."
        )

        if ask_llm is None:
            return ""

        raw_sql = ask_llm(prompt)

        repaired_sql = clean_sql(raw_sql)

        print("[REPAIRED SQL]")
        print(repaired_sql)

        return repaired_sql

    except Exception as e:

        print(
            "[REPAIR ERROR]:",
            e
        )

        return ""


# ============================================================
# EXECUTE SQL WITH RETRY
# ============================================================

def execute_sql_with_retry(
    question,
    sql,
    max_retries=3
):

    current_sql = clean_sql(sql)

    last_error = None

    for attempt in range(
        max_retries + 1
    ):

        print(
            f"[SQL ATTEMPT] {attempt + 1}"
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

            repaired_sql = repair_sql(
                question,
                current_sql,
                last_error
            )

            if not repaired_sql:
                break

            current_sql = repaired_sql

    return {
        "success": False,
        "data": None,
        "sql": current_sql,
        "error": last_error
    }


# ============================================================
# FORMAT SQL RESULT
# ============================================================

def format_business_answer(
    question,
    data
):

    if not data:

        return (
            "No matching records were found."
        )

    result_text = ""

    for index, row in enumerate(
        data,
        start=1
    ):

        result_text += (
            f"Record {index}: {row}\n"
        )

    prompt = f"""
You are an AI Business Assistant.

Convert the database result into a simple,
clear business answer.

================================================
QUESTION
================================================

{question}

================================================
DATABASE RESULT
================================================

{result_text}

================================================
RULES
================================================

1. Use ONLY the supplied database result.

2. Never invent information.

3. Answer exactly what the user asked.

4. If the user asks "which", show actual
   names/items from the result.

5. If the user asks "who", show actual
   customer/person names from the result.

6. If the user asks for TOP N, show ALL
   requested records.

7. If the user asks "how many", clearly
   give the count.

8. For low stock questions, show product,
   stock quantity and reorder level.

9. For expensive products, show product
   name and price.

10. For customer spending questions,
    show customer name and spending.

11. For complex customer/product questions,
    clearly connect the customer with the
    products returned.

12. Do not show Python dictionaries.

13. Do not show SQL.

14. Keep the answer easy to understand.

15. Use bullet points for multiple records.

16. Use ₹ when a value represents
    Indian currency.

17. Never add information that is not
    present in the database result.

Return ONLY the final business answer.
"""

    try:

        if ask_llm is None:

            raise RuntimeError(
                "LLM is not available."
            )

        answer = ask_llm(prompt)

        return answer.strip()

    except Exception as e:

        print(
            "[ANSWER FORMAT ERROR]:",
            e
        )

        lines = []

        for row in data:

            values = []

            for key, value in row.items():

                values.append(
                    f"{key}: {value}"
                )

            lines.append(
                " | ".join(values)
            )

        return "\n".join(lines)


# ============================================================
# RAG ANSWER
# ============================================================

def format_rag_answer(
    question,
    context
):

    if not context:

        return (
            "I could not find relevant information "
            "in the business documents."
        )

    prompt = f"""
You are an AI Business Assistant.

Answer the user's question using ONLY
the provided business documents.

================================================
QUESTION
================================================

{question}

================================================
DOCUMENT INFORMATION
================================================

{context}

================================================
RULES
================================================

1. Do not invent information.

2. Use only the provided documents.

3. Keep the answer simple.

4. If the answer is not available,
   clearly say so.

Return ONLY the answer.
"""

    try:

        if ask_llm is None:

            return str(context)

        return ask_llm(prompt).strip()

    except Exception as e:

        print(
            "[RAG ANSWER ERROR]:",
            e
        )

        return str(context)


# ============================================================
# MAIN ROUTER
# ============================================================

def route_question(question):

    question = question.strip()

    print(
        "\n=========================================="
    )

    print(
        "[ROUTER RECEIVED]:",
        question
    )

    print(
        "=========================================="
    )

    # ========================================================
    # EMPTY QUESTION
    # ========================================================

    if not question:

        return {
            "type": "unknown",
            "data": None,
            "sql": None,
            "answer": (
                "Please enter a business question."
            )
        }

    # ========================================================
    # DATABASE OVERVIEW
    # ========================================================

    if is_database_overview_question(
        question
    ):

        print(
            "🔥 DATABASE OVERVIEW DETECTED 🔥"
        )

        try:

            answer = (
                generate_database_overview(
                    question
                )
            )

            return {
                "type": "database_overview",
                "data": None,
                "sql": None,
                "answer": answer
            }

        except Exception as e:

            print(
                "[OVERVIEW ERROR]:",
                e
            )

            return {
                "type": "error",
                "data": None,
                "sql": None,
                "message": (
                    f"Database overview error: {e}"
                )
            }

    # ========================================================
    # CLASSIFICATION
    # ========================================================

    route_type = classify_question(
        question
    )

    print(
        "[ROUTER] Question type:",
        route_type
    )

    # ========================================================
    # SQL ROUTE
    # ========================================================

    if route_type == "sql":

        print(
            "[ROUTER] Generating SQL..."
        )

        sql = generate_sql(
            question
        )

        if not sql:

            return {
                "type": "error",
                "data": None,
                "sql": None,
                "message": (
                    "Unable to generate SQL "
                    "for this business question."
                )
            }

        result = execute_sql_with_retry(
            question,
            sql,
            max_retries=3
        )

        if result["success"]:

            answer = (
                format_business_answer(
                    question,
                    result["data"]
                )
            )

            return {
                "type": "sql",
                "data": result["data"],
                "sql": result["sql"],
                "attempt": result["attempt"],
                "answer": answer
            }

        return {
            "type": "error",
            "data": None,
            "sql": result["sql"],
            "message": result["error"],
            "answer": (
                "I could not generate a valid query "
                "for that question."
            )
        }

    # ========================================================
    # RAG ROUTE
    # ========================================================

    if route_type == "rag":

        print(
            "[ROUTER] Retrieving business documents..."
        )

        if retrieve_context is None:

            return {
                "type": "error",
                "data": None,
                "sql": None,
                "message": (
                    "RAG pipeline is not available."
                )
            }

        try:

            context = retrieve_context(
                question,
                n_results=5
            )

            answer = format_rag_answer(
                question,
                context
            )

            return {
                "type": "rag",
                "data": {
                    "question": question,
                    "context": context
                },
                "sql": None,
                "answer": answer
            }

        except Exception as e:

            print(
                "[RAG ERROR]:",
                e
            )

            return {
                "type": "error",
                "data": None,
                "sql": None,
                "message": str(e)
            }

    # ========================================================
    # FALLBACK
    # ========================================================

    print(
        "[ROUTER] Unknown question."
    )

    return {
        "type": "unknown",
        "data": None,
        "sql": None,
        "answer": (
            "I couldn't understand the question. "
            "Please ask a business-related question."
        )
    }


# ============================================================
# TERMINAL TEST MODE
# ============================================================

if __name__ == "__main__":

    print(
        "=========================================="
    )

    print(
        "🤖 AI BUSINESS ASSISTANT"
    )

    print(
        "=========================================="
    )

    while True:

        question = input(
            "\nAsk a business question "
            "(type 'exit' to stop): "
        )

        if question.lower().strip() == "exit":
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
                result.get(
                    "message",
                    "No answer available."
                )
            )
        )

        if result.get("sql"):

            print(
                "\n========== SQL =========="
            )

            print(
                result["sql"]
            )

        if result.get("data") is not None:

            print(
                "\n========== ROWS =========="
            )

            print(
                result["data"]
            )