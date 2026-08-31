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
# DATABASE ENGINE
# ============================================================

def get_engine():

    session = SessionLocal()

    try:
        return session.get_bind()

    finally:
        session.close()


# ============================================================
# REAL DATABASE TABLES
# ============================================================

def get_real_database_tables():

    session = SessionLocal()

    try:

        engine = session.get_bind()
        inspector = inspect(engine)

        return sorted(
            inspector.get_table_names()
        )

    except Exception as e:

        print("[TABLE ERROR]", e)
        return []

    finally:
        session.close()


# ============================================================
# DATABASE COLUMNS
# ============================================================

def get_database_columns():

    session = SessionLocal()

    try:

        engine = session.get_bind()
        inspector = inspect(engine)

        result = {}

        for table in inspector.get_table_names():

            result[table] = [
                column["name"]
                for column in inspector.get_columns(table)
            ]

        return result

    except Exception as e:

        print("[COLUMN ERROR]", e)
        return {}

    finally:
        session.close()


# ============================================================
# FIND TABLE
# ============================================================

def find_table(
    tables,
    candidates
):

    lower_map = {
        table.lower(): table
        for table in tables
    }

    # Exact match first
    for candidate in candidates:

        if candidate.lower() in lower_map:

            return lower_map[
                candidate.lower()
            ]

    # Partial match second
    for candidate in candidates:

        candidate_lower = candidate.lower()

        for table in tables:

            if candidate_lower in table.lower():

                return table

    return None


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(
    columns,
    candidates
):

    lower_map = {
        column.lower(): column
        for column in columns
    }

    # Exact match
    for candidate in candidates:

        if candidate.lower() in lower_map:

            return lower_map[
                candidate.lower()
            ]

    # Partial match
    for candidate in candidates:

        candidate_lower = candidate.lower()

        for column in columns:

            if candidate_lower in column.lower():

                return column

    return None


# ============================================================
# DATABASE SCHEMA
# ============================================================

def get_database_schema():

    session = SessionLocal()

    try:

        engine = session.get_bind()
        inspector = inspect(engine)

        tables = inspector.get_table_names()

        if not tables:

            return ""

        schema = []

        schema.append(
            "REAL DATABASE SCHEMA"
        )

        schema.append(
            "=" * 90
        )

        # ----------------------------------------------------
        # TABLES / COLUMNS
        # ----------------------------------------------------

        for table in sorted(tables):

            schema.append("")
            schema.append(
                f"TABLE: {table}"
            )

            try:

                columns = inspector.get_columns(
                    table
                )

                for column in columns:

                    name = column.get(
                        "name"
                    )

                    data_type = str(
                        column.get(
                            "type",
                            ""
                        )
                    )

                    nullable = column.get(
                        "nullable",
                        True
                    )

                    schema.append(
                        f"  COLUMN: {name} | "
                        f"TYPE: {data_type} | "
                        f"NULLABLE: {nullable}"
                    )

            except Exception as e:

                print(
                    f"[COLUMN ERROR] {table}: {e}"
                )

        # ----------------------------------------------------
        # PRIMARY KEYS
        # ----------------------------------------------------

        schema.append("")
        schema.append(
            "PRIMARY KEYS"
        )
        schema.append(
            "=" * 90
        )

        for table in sorted(tables):

            try:

                pk = inspector.get_pk_constraint(
                    table
                )

                columns = (
                    pk.get(
                        "constrained_columns"
                    )
                    or []
                )

                if columns:

                    schema.append(
                        f"{table}: "
                        f"{', '.join(columns)}"
                    )

            except Exception as e:

                print(
                    f"[PK WARNING] {table}: {e}"
                )

        # ----------------------------------------------------
        # FOREIGN KEYS
        # ----------------------------------------------------

        schema.append("")
        schema.append(
            "FOREIGN KEY RELATIONSHIPS"
        )
        schema.append(
            "=" * 90
        )

        for table in sorted(tables):

            try:

                foreign_keys = (
                    inspector.get_foreign_keys(
                        table
                    )
                )

                for fk in foreign_keys:

                    local_columns = (
                        fk.get(
                            "constrained_columns"
                        )
                        or []
                    )

                    remote_table = fk.get(
                        "referred_table"
                    )

                    remote_columns = (
                        fk.get(
                            "referred_columns"
                        )
                        or []
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
# DATABASE INFORMATION
# ============================================================

def get_database_information():

    session = SessionLocal()

    try:

        engine = session.get_bind()
        inspector = inspect(engine)

        tables = inspector.get_table_names()

        information = []

        for table in sorted(tables):

            columns = [
                column["name"]
                for column in inspector.get_columns(
                    table
                )
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

            information.append(
                {
                    "table": table,
                    "columns": columns,
                    "rows": count
                }
            )

        return information

    except Exception as e:

        print(
            "[DATABASE INFORMATION ERROR]",
            e
        )

        return []

    finally:
        session.close()


# ============================================================
# DATABASE STRUCTURE QUESTIONS
# ============================================================

def handle_database_structure_question(
    question
):

    q = question.lower().strip()

    # --------------------------------------------------------
    # TABLE COUNT
    # --------------------------------------------------------

    table_count_patterns = [

        r"\bhow many tables\b",
        r"\bhow many table\b",
        r"\bnumber of tables\b",
        r"\bnumber of table\b",
        r"\btotal tables\b",
        r"\btotal number of tables\b",
        r"\bhow much tables\b",
        r"\bhow many database tables\b"

    ]

    if any(
        re.search(
            pattern,
            q
        )
        for pattern in table_count_patterns
    ):

        tables = get_real_database_tables()

        return {

            "type":
                "database_overview",

            "data": {
                "table_count":
                    len(tables),
                "tables":
                    tables
            },

            "sql": None,

            "intent":
                "count database tables",

            "answer":
                f"We have {len(tables)} "
                f"tables in the database."

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
        r"\blist database tables\b"

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

                "type":
                    "database_overview",

                "data": None,

                "sql": None,

                "intent":
                    "list database tables",

                "answer":
                    "I could not find any tables "
                    "in the database."

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

            "type":
                "database_overview",

            "data": {
                "table_count":
                    len(tables),
                "tables":
                    tables
            },

            "sql": None,

            "intent":
                "list database tables",

            "answer":
                answer

        }

    # --------------------------------------------------------
    # STRUCTURE
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
        "database details",
        "database overview"

    ]

    if any(
        phrase in q
        for phrase in structure_patterns
    ):

        information = (
            get_database_information()
        )

        if not information:

            return {

                "type":
                    "database_overview",

                "data": None,

                "sql": None,

                "intent":
                    "database structure",

                "answer":
                    "I could not read the "
                    "database structure."

            }

        answer = (
            "## Database Structure\n\n"
            f"The database contains "
            f"**{len(information)} tables**.\n\n"
        )

        for item in information:

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

            "type":
                "database_overview",

            "data":
                information,

            "sql": None,

            "intent":
                "database structure",

            "answer":
                answer

        }

    return None


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(response):

    if not response:

        return None

    raw = str(response).strip()

    raw = re.sub(
        r"```json",
        "",
        raw,
        flags=re.IGNORECASE
    )

    raw = re.sub(
        r"```",
        "",
        raw
    ).strip()

    try:

        result = json.loads(raw)

        if isinstance(result, dict):

            return result

    except Exception:
        pass

    start = raw.find("{")
    end = raw.rfind("}")

    if (
        start != -1
        and end != -1
        and end > start
    ):

        try:

            result = json.loads(
                raw[start:end + 1]
            )

            if isinstance(result, dict):

                return result

        except Exception:
            pass

    return None


# ============================================================
# RECORD LEVEL QUESTION
# ============================================================

def is_record_level_question(
    question
):

    q = question.lower().strip()

    patterns = [

        r"\bwho\b",
        r"\bwhich\b",
        r"\bwhat products\b",
        r"\bwhat customers\b",
        r"\bwhat orders\b",
        r"\bwhich products\b",
        r"\bwhich customers\b",
        r"\bwhich orders\b",
        r"\bwho are\b",
        r"\blist\b",
        r"\bshow me\b",
        r"\bshow the\b",
        r"\bshow all\b",
        r"\bmention\b",
        r"\bgive me the names\b",
        r"\bname the\b",
        r"\bnames of\b",
        r"\bdetails of\b",
        r"\bdetails about\b",
        r"\bprovide details\b"

    ]

    return any(
        re.search(
            pattern,
            q
        )
        for pattern in patterns
    )


# ============================================================
# COUNT + DETAILS
# ============================================================

def wants_count_and_details(
    question
):

    q = question.lower()

    count_words = [

        "how many",
        "number of",
        "count"

    ]

    detail_words = [

        "mention",
        "name",
        "names",
        "details",
        "show",
        "list",
        "give me",
        "include",
        "with their",
        "along with"

    ]

    has_count = any(
        word in q
        for word in count_words
    )

    has_details = any(
        word in q
        for word in detail_words
    )

    return (
        has_count
        and has_details
    )


# ============================================================
# AGGREGATION
# ============================================================

def is_aggregation_question(
    question
):

    q = question.lower()

    patterns = [

        r"\bhow many\b",
        r"\bnumber of\b",
        r"\bcount\b",
        r"\btotal\b",
        r"\bsum\b",
        r"\baverage\b",
        r"\bavg\b",
        r"\bmean\b",
        r"\bmaximum\b",
        r"\bminimum\b",
        r"\bhighest\b",
        r"\blowest\b",
        r"\bmost\b",
        r"\bleast\b",
        r"\btop\b",
        r"\bbottom\b",
        r"\branking\b"

    ]

    return any(
        re.search(
            pattern,
            q
        )
        for pattern in patterns
    )


# ============================================================
# UNDERSTAND QUESTION
# ============================================================

def understand_question(
    question
):

    schema = get_database_schema()

    prompt = f"""
You are the router of an ERP AI Business Assistant.

Classify the user's question.

Use SQL for all live database/business information.

Use RAG only for company documents, policies,
manuals, procedures and uploaded business documents.

Use DATABASE_OVERVIEW only for database structure.

User question:

{question}

REAL DATABASE SCHEMA:

{schema}

Return ONLY JSON:

{{
    "route": "SQL",
    "intent": "short semantic description",
    "needs_database": true,
    "needs_documents": false
}}
"""

    if ask_llm is None:

        return {

            "route": "SQL",

            "intent":
                "business database question",

            "needs_database": True,

            "needs_documents": False

        }

    try:

        response = ask_llm(
            prompt
        )

        print(
            "\n[ROUTER RESPONSE]"
        )

        print(response)

        result = extract_json(
            response
        )

        if not result:

            raise ValueError(
                "Invalid router JSON"
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
                    "business database question"
                )
            ),

            "needs_database":
                bool(
                    result.get(
                        "needs_database",
                        route == "SQL"
                    )
                ),

            "needs_documents":
                bool(
                    result.get(
                        "needs_documents",
                        route == "RAG"
                    )
                )

        }

    except Exception as e:

        print(
            "[ROUTER ERROR]",
            e
        )

        return {

            "route": "SQL",

            "intent":
                "business database question",

            "needs_database": True,

            "needs_documents": False

        }


# ============================================================
# CONTROLLED SQL BUILDERS
# ============================================================

def build_complex_controlled_sql(
    question
):

    q = question.lower()

    tables = get_real_database_tables()
    columns = get_database_columns()

    # ========================================================
    # FIND REAL TABLES
    # ========================================================

    customers = find_table(
        tables,
        [
            "customers",
            "customer"
        ]
    )

    orders = find_table(
        tables,
        [
            "orders",
            "order"
        ]
    )

    order_items = find_table(
        tables,
        [
            "order_items",
            "order_item",
            "orderitems"
        ]
    )

    products = find_table(
        tables,
        [
            "products",
            "product"
        ]
    )

    payments = find_table(
        tables,
        [
            "payments",
            "payment"
        ]
    )

    if not all([
        customers,
        orders,
        order_items,
        products
    ]):

        return None

    # ========================================================
    # REAL COLUMNS
    # ========================================================

    customer_cols = columns.get(
        customers,
        []
    )

    order_cols = columns.get(
        orders,
        []
    )

    item_cols = columns.get(
        order_items,
        []
    )

    product_cols = columns.get(
        products,
        []
    )

    payment_cols = columns.get(
        payments,
        []
    ) if payments else []

    customer_id = find_column(
        customer_cols,
        [
            "customer_id",
            "id"
        ]
    )

    customer_name = find_column(
        customer_cols,
        [
            "customer_name",
            "name",
            "full_name"
        ]
    )

    order_id = find_column(
        order_cols,
        [
            "order_id",
            "id"
        ]
    )

    order_customer_id = find_column(
        order_cols,
        [
            "customer_id"
        ]
    )

    item_order_id = find_column(
        item_cols,
        [
            "order_id"
        ]
    )

    item_product_id = find_column(
        item_cols,
        [
            "product_id"
        ]
    )

    product_id = find_column(
        product_cols,
        [
            "product_id",
            "id"
        ]
    )

    product_name = find_column(
        product_cols,
        [
            "product_name",
            "name"
        ]
    )

    stock_quantity = find_column(
        product_cols,
        [
            "stock_quantity",
            "stock",
            "quantity_in_stock"
        ]
    )

    reorder_level = find_column(
        product_cols,
        [
            "reorder_level",
            "reorder_point",
            "minimum_stock"
        ]
    )

    payment_order_id = find_column(
        payment_cols,
        [
            "order_id"
        ]
    )

    payment_status = find_column(
        payment_cols,
        [
            "payment_status",
            "status"
        ]
    )

    # ========================================================
    # QUESTION 1
    #
    # CUSTOMERS:
    # more orders than average customer
    # pending payment
    # low-stock product
    # ========================================================

    customer_complex = (

        (
            "average customer" in q
            or "average order count" in q
        )

        and
        (
            "pending payment" in q
            or "pending payments" in q
        )

        and
        (
            "below the reorder level" in q
            or "below reorder level" in q
            or "low stock" in q
        )

        and
        (
            "customer" in q
        )

    )

    if customer_complex:

        required = [

            customer_id,
            order_id,
            order_customer_id,
            item_order_id,
            item_product_id,
            product_id,
            stock_quantity,
            reorder_level
        ]

        if not all(required):

            print(
                "[CONTROLLED SQL] "
                "Required columns missing."
            )

            return None

        # ----------------------------------------------------
        # Payment is required for pending condition
        # ----------------------------------------------------

        if not payments:

            return None

        if not all([
            payment_order_id,
            payment_status
        ]):

            return None

        # ----------------------------------------------------
        # Customer name fallback
        # ----------------------------------------------------

        if not customer_name:

            customer_name = customer_id

        sql = f"""
WITH customer_order_counts AS (

    SELECT
        o.`{order_customer_id}` AS customer_id,
        COUNT(DISTINCT o.`{order_id}`) AS order_count

    FROM `{orders}` o

    GROUP BY
        o.`{order_customer_id}`
),

average_customer_orders AS (

    SELECT
        AVG(order_count * 1.0) AS average_order_count

    FROM customer_order_counts
),

qualifying_customers AS (

    SELECT
        coc.customer_id,
        coc.order_count,
        aco.average_order_count

    FROM customer_order_counts coc

    CROSS JOIN average_customer_orders aco

    WHERE coc.order_count >
          aco.average_order_count

    AND EXISTS (

        SELECT 1

        FROM `{orders}` po

        INNER JOIN `{payments}` pp
            ON pp.`{payment_order_id}`
             = po.`{order_id}`

        WHERE po.`{order_customer_id}`
              = coc.customer_id

        AND LOWER(
            CAST(
                pp.`{payment_status}` AS TEXT
            )
        ) = 'pending'
    )
)

SELECT DISTINCT

    c.`{customer_name}` AS customer_name,

    qc.order_count AS order_count,

    qc.average_order_count
        AS average_order_count,

    o.`{order_id}` AS order_id,

    p.`{product_name}` AS product_name,

    pay.`{payment_status}`
        AS payment_status,

    p.`{stock_quantity}`
        AS stock_quantity

FROM qualifying_customers qc

INNER JOIN `{customers}` c
    ON c.`{customer_id}`
       = qc.customer_id

INNER JOIN `{orders}` o
    ON o.`{order_customer_id}`
       = qc.customer_id

INNER JOIN `{order_items}` oi
    ON oi.`{item_order_id}`
       = o.`{order_id}`

INNER JOIN `{products}` p
    ON p.`{product_id}`
       = oi.`{item_product_id}`

INNER JOIN `{payments}` pay
    ON pay.`{payment_order_id}`
       = o.`{order_id}`

WHERE p.`{stock_quantity}`
      <= p.`{reorder_level}`

AND LOWER(
    CAST(
        pay.`{payment_status}` AS TEXT
    )
) = 'pending'

ORDER BY
    qc.order_count DESC,
    c.`{customer_name}`,
    o.`{order_id}`
"""

        print(
            "\n[CONTROLLED SQL]"
        )

        print(
            sql
        )

        return sql.strip()

    # ========================================================
    # QUESTION 2
    #
    # PRODUCTS:
    # low stock
    # ordered by multiple customers
    # revenue > 1000
    # ========================================================

    product_complex = (

        (
            "low stock" in q
            or "below the reorder level" in q
            or "below reorder level" in q
        )

        and
        (
            "multiple customers" in q
            or "more than one customer" in q
            or "different customers" in q
            or "multiple customer" in q
        )

        and
        (
            "revenue" in q
            or "sales" in q
        )

    )

    if product_complex:

        required = [

            product_id,
            product_name,
            stock_quantity,
            reorder_level,
            item_order_id,
            item_product_id,
            order_id,
            order_customer_id
        ]

        if not all(required):

            return None

        if not customer_id:

            return None

        # ----------------------------------------------------
        # Find revenue fields
        # ----------------------------------------------------

        quantity = find_column(
            item_cols,
            [
                "quantity",
                "qty",
                "item_quantity"
            ]
        )

        unit_price = find_column(
            item_cols,
            [
                "unit_price",
                "price",
                "item_price",
                "selling_price"
            ]
        )

        line_total = find_column(
            item_cols,
            [
                "line_total",
                "subtotal",
                "total_price",
                "amount",
                "item_total"
            ]
        )

        # ----------------------------------------------------
        # Product revenue expression
        # ----------------------------------------------------

        revenue_expression = None

        if line_total:

            revenue_expression = (
                f"oi.`{line_total}`"
            )

        elif quantity and unit_price:

            revenue_expression = (
                f"oi.`{quantity}` "
                f"* oi.`{unit_price}`"
            )

        else:

            # Try product price if order_items only
            # contains quantity.

            product_price = find_column(
                product_cols,
                [
                    "unit_price",
                    "price",
                    "selling_price"
                ]
            )

            if quantity and product_price:

                revenue_expression = (
                    f"oi.`{quantity}` "
                    f"* p.`{product_price}`"
                )

        if revenue_expression:

            sql = f"""
SELECT

    p.`{product_name}`
        AS product_name,

    p.`{stock_quantity}`
        AS stock_quantity,

    COUNT(DISTINCT o.`{order_customer_id}`)
        AS customer_count,

    SUM(
        {revenue_expression}
    ) AS revenue

FROM `{products}` p

INNER JOIN `{order_items}` oi
    ON oi.`{item_product_id}`
       = p.`{product_id}`

INNER JOIN `{orders}` o
    ON o.`{order_id}`
       = oi.`{item_order_id}`

WHERE p.`{stock_quantity}`
      <= p.`{reorder_level}`

GROUP BY

    p.`{product_id}`,
    p.`{product_name}`,
    p.`{stock_quantity}`

HAVING
    COUNT(
        DISTINCT o.`{order_customer_id}`
    ) > 1

AND
    SUM(
        {revenue_expression}
    ) > 1000

ORDER BY
    revenue DESC
"""

            print(
                "\n[CONTROLLED PRODUCT SQL]"
            )

            print(sql)

            return sql.strip()

        # ----------------------------------------------------
        # If product revenue cannot be calculated safely,
        # let LLM handle it.
        # ----------------------------------------------------

        print(
            "[CONTROLLED SQL] "
            "No product-level revenue field found."
        )

    return None


# ============================================================
# CLEAN SQL
# ============================================================

def clean_sql(raw_sql):

    if not raw_sql:

        return ""

    sql = str(
        raw_sql
    ).strip()

    sql = re.sub(
        r"```sql",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```mysql",
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

    sql = sql[
        match.start():
    ]

    semicolon = sql.find(";")

    if semicolon != -1:

        sql = sql[
            :semicolon
        ]

    return sql.strip()


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(
    question,
    intent=""
):

    # ========================================================
    # FIRST TRY CONTROLLED SQL
    # ========================================================

    controlled_sql = (
        build_complex_controlled_sql(
            question
        )
    )

    if controlled_sql:

        print(
            "\n[SQL SOURCE] "
            "CONTROLLED COMPLEX SQL"
        )

        return controlled_sql

    # ========================================================
    # OTHERWISE LLM
    # ========================================================

    schema = get_database_schema()

    if not schema:

        print(
            "[SQL] Database schema unavailable."
        )

        return ""

    record_level = (
        is_record_level_question(
            question
        )
    )

    count_and_details = (
        wants_count_and_details(
            question
        )
    )

    if (
        record_level
        or count_and_details
    ):

        output_mode = """

RECORD / DETAIL MODE

Return actual matching records.

Do NOT return only COUNT(*).

Return every field explicitly requested
by the user.

If the question contains an aggregate
condition, use GROUP BY and HAVING where
necessary while still returning the
requested entity details.

"""

    else:

        output_mode = """

AGGREGATION / ANALYSIS MODE

Use COUNT, SUM, AVG, MIN, MAX,
GROUP BY, HAVING and ORDER BY when
required.

"""

    prompt = f"""
You are an expert Text-to-SQL engine
for a REAL ERP database.

Generate ONE executable SELECT query.

============================================================
USER QUESTION
============================================================

{question}

============================================================
SEMANTIC INTENT
============================================================

{intent}

============================================================
REAL DATABASE SCHEMA
============================================================

{schema}

============================================================
MODE
============================================================

{output_mode}

============================================================
IMPORTANT
============================================================

Answer the COMPLETE question.

Never simplify a complex question.

Never invent tables.

Never invent columns.

Never invent relationships.

Use only tables and columns present
in the REAL DATABASE SCHEMA.

============================================================
LOW STOCK
============================================================

If stock_quantity and reorder_level
exist:

stock_quantity <= reorder_level

============================================================
PENDING PAYMENT
============================================================

Inspect the actual payment table.

The payment status may be called
status or payment_status.

Use the actual schema column.

============================================================
AVERAGE CUSTOMER ORDER COUNT
============================================================

If the user asks for customers who
placed more orders than the average
customer:

FIRST calculate each customer's
order count:

COUNT(DISTINCT orders.order_id)

Then calculate:

AVG(customer_order_count)

Then compare:

customer_order_count >
average_customer_order_count

Do NOT create a correlated query such as:

SELECT AVG(count)
FROM (
    SELECT COUNT(...)
    FROM orders
)

Instead use a separate grouped
customer-count query/CTE.

============================================================
MULTIPLE CUSTOMERS
============================================================

For products ordered by multiple
customers:

COUNT(DISTINCT orders.customer_id) > 1

Use only if customer_id actually exists.

============================================================
REVENUE
============================================================

For product-level revenue, prefer
order_items line amount or:

quantity * unit_price

Do NOT multiply orders.total_amount
by order_items.quantity.

============================================================
FINAL
============================================================

Return ONLY SQL.

NO markdown.

NO explanation.
"""

    if ask_llm is None:

        return ""

    try:

        response = ask_llm(
            prompt
        )

        sql = clean_sql(
            response
        )

        print(
            "\n[GENERATED SQL]"
        )

        print(sql)

        return sql

    except Exception as e:

        print(
            "[SQL GENERATION ERROR]",
            e
        )

        return ""


# ============================================================
# SQL VALIDATION
# ============================================================

def validate_sql(sql):

    if not sql:

        return (
            False,
            "SQL query is empty."
        )

    sql_clean = sql.strip()

    upper = sql_clean.upper()

    if not re.match(
        r"^\s*SELECT\b",
        upper
    ):

        return (
            False,
            "Only SELECT queries are allowed."
        )

    if ";" in sql_clean:

        return (
            False,
            "Multiple SQL statements are not allowed."
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
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    valid, error = validate_sql(
        sql
    )

    if not valid:

        raise ValueError(
            error
        )

    session = SessionLocal()

    try:

        print(
            "\n[DATABASE] EXECUTING SQL"
        )

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
            "[DATABASE] ROWS:",
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

    # ========================================================
    # TRY CONTROLLED SQL AGAIN
    # ========================================================

    controlled_sql = (
        build_complex_controlled_sql(
            question
        )
    )

    if controlled_sql:

        print(
            "\n[REPAIR] "
            "Using controlled SQL."
        )

        return controlled_sql

    # ========================================================
    # LLM REPAIR
    # ========================================================

    schema = get_database_schema()

    if not schema:

        return ""

    prompt = f"""
You are an expert SQL debugger.

Repair the failed SELECT query.

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

Rules:

1. Use only real tables.
2. Use only real columns.
3. Use only real foreign keys.
4. Preserve every condition.
5. Preserve every requested output field.
6. Do not turn record questions into COUNT only.
7. Use HAVING for aggregate conditions.
8. Use WHERE for normal conditions.
9. For average customer order count,
   calculate each customer's order count
   first and then AVG that grouped result.
10. Do not create invalid correlated
    aggregate subqueries.
11. SELECT only.

Return ONLY the corrected SELECT query.
"""

    if ask_llm is None:

        return ""

    try:

        response = ask_llm(
            prompt
        )

        sql = clean_sql(
            response
        )

        print(
            "\n[REPAIRED SQL]"
        )

        print(sql)

        return sql

    except Exception as e:

        print(
            "[REPAIR ERROR]",
            e
        )

        return ""


# ============================================================
# EXECUTE + RETRY
# ============================================================

def execute_sql_with_retry(
    question,
    intent,
    sql,
    max_retries=5
):

    current_sql = sql

    last_error = None

    attempted_sql = []

    for attempt in range(
        max_retries + 1
    ):

        print(
            f"\n========== SQL ATTEMPT "
            f"{attempt + 1} =========="
        )

        print(current_sql)

        if not current_sql:

            break

        if current_sql in attempted_sql:

            print(
                "[SQL] Same query already attempted."
            )

            break

        attempted_sql.append(
            current_sql
        )

        try:

            data = execute_sql(
                current_sql
            )

            return {

                "success": True,

                "data": data,

                "sql": current_sql,

                "attempt":
                    attempt + 1,

                "error": None

            }

        except Exception as e:

            last_error = str(e)

            print(
                "\n[SQL ERROR]"
            )

            print(
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

            valid, validation_error = (
                validate_sql(
                    repaired
                )
            )

            if not valid:

                print(
                    "[REPAIRED SQL INVALID]",
                    validation_error
                )

                current_sql = repaired

                continue

            current_sql = repaired

    return {

        "success": False,

        "data": None,

        "sql": current_sql,

        "attempt":
            len(attempted_sql),

        "error":
            last_error

    }


# ============================================================
# EMPTY RESULT
# ============================================================

def answer_empty_result(
    question="",
    intent=""
):

    return (
        "No matching records were found "
        "in the database."
    )


# ============================================================
# FORMAT RECORD RESULTS
# ============================================================

def format_record_results(
    data
):

    if not data:

        return answer_empty_result()

    lines = []

    for index, row in enumerate(
        data,
        start=1
    ):

        lines.append(
            f"**Record {index}**"
        )

        for key, value in row.items():

            if value is None:

                value = "N/A"

            label = str(key)

            label = label.replace(
                "_",
                " "
            )

            label = label.title()

            lines.append(
                f"**{label}:** {value}"
            )

        lines.append("")

    return "\n".join(
        lines
    )


# ============================================================
# FORMAT BUSINESS ANSWER
# ============================================================

def format_business_answer(
    question,
    intent,
    data
):

    if not data:

        return answer_empty_result(
            question,
            intent
        )

    record_level = (
        is_record_level_question(
            question
        )
        or
        wants_count_and_details(
            question
        )
    )

    if record_level:

        return format_record_results(
            data
        )

    if ask_llm is None:

        return "\n".join(

            " | ".join(
                f"{key}: {value}"
                for key, value in row.items()
            )

            for row in data
        )

    max_rows = 200

    visible_data = data[
        :max_rows
    ]

    result_text = "\n".join(

        f"Record {index}: {row}"

        for index, row in enumerate(
            visible_data,
            start=1
        )

    )

    if len(data) > max_rows:

        result_text += (
            f"\n... and "
            f"{len(data) - max_rows} "
            f"additional records."
        )

    prompt = f"""
You are the final answer generator
for an AI Business Assistant.

Answer using ONLY the database result.

USER QUESTION:

{question}

INTENT:

{intent}

DATABASE RESULT:

{result_text}

Rules:

1. Database result is the source of truth.
2. Do not invent information.
3. Do not change values.
4. Do not remove requested information.
5. Clearly explain counts.
6. Clearly explain totals.
7. Clearly explain averages.
8. List multiple records clearly.
9. Preserve ranking order.
10. Do not show Python dictionaries.
11. Do not show SQL.
12. Do not mention routing.
13. Do not claim query failure when data exists.

Return ONLY the natural-language answer.
"""

    try:

        answer = ask_llm(
            prompt
        ).strip()

        if answer:

            return answer

    except Exception as e:

        print(
            "[ANSWER ERROR]",
            e
        )

    return "\n".join(

        " | ".join(
            f"{key}: {value}"
            for key, value in row.items()
        )

        for row in data
    )


# ============================================================
# RAG CONTEXT
# ============================================================

def retrieve_rag_context(
    question
):

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
# RAG ANSWER
# ============================================================

def format_rag_answer(
    question,
    intent,
    context
):

    if not context:

        return (
            "I could not find relevant "
            "information in the business documents."
        )

    prompt = f"""
You are the document-answering component
of an AI Business Assistant.

Answer using ONLY the retrieved
business-document context.

USER QUESTION:

{question}

INTENT:

{intent}

DOCUMENT CONTEXT:

{context}

Rules:

1. Do not invent information.
2. Do not use database information.
3. Do not assume facts not present.
4. If the answer is not present,
   say so clearly.
5. Answer naturally and directly.

Return ONLY the answer.
"""

    if ask_llm is None:

        return str(context)

    try:

        answer = ask_llm(
            prompt
        ).strip()

        if answer:

            return answer

    except Exception as e:

        print(
            "[RAG ANSWER ERROR]",
            e
        )

    return str(context)


# ============================================================
# MAIN ROUTER
# ============================================================

def route_question(
    question
):

    question = str(
        question
    ).strip()

    print(
        "\n=============================================="
    )

    print(
        "[USER QUESTION]",
        question
    )

    print(
        "=============================================="
    )

    # ========================================================
    # EMPTY
    # ========================================================

    if not question:

        return {

            "type": "unknown",

            "data": None,

            "sql": None,

            "intent": "",

            "answer":
                "Please enter a question."

        }

    # ========================================================
    # DATABASE STRUCTURE
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

        return structure_result

    # ========================================================
    # UNDERSTAND QUESTION
    # ========================================================

    understanding = (
        understand_question(
            question
        )
    )

    route = understanding.get(
        "route",
        "SQL"
    )

    intent = understanding.get(
        "intent",
        "business database question"
    )

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

        information = (
            get_database_information()
        )

        if not information:

            return {

                "type":
                    "database_overview",

                "data": None,

                "sql": None,

                "intent":
                    intent,

                "answer":
                    "I could not read "
                    "the database."

            }

        answer = (
            f"The database contains "
            f"{len(information)} tables.\n\n"
        )

        for item in information:

            answer += (
                f"- {item['table']}: "
                f"{item['rows']} records\n"
            )

        return {

            "type":
                "database_overview",

            "data":
                information,

            "sql": None,

            "intent":
                intent,

            "answer":
                answer

        }

    # ========================================================
    # RAG
    # ========================================================

    if route == "RAG":

        try:

            context = (
                retrieve_rag_context(
                    question
                )
            )

            answer = (
                format_rag_answer(
                    question,
                    intent,
                    context
                )
            )

            return {

                "type":
                    "rag",

                "data": {

                    "question":
                        question,

                    "context":
                        context

                },

                "sql": None,

                "intent":
                    intent,

                "answer":
                    answer

            }

        except Exception as e:

            print(
                "[RAG ERROR]",
                e
            )

            return {

                "type":
                    "error",

                "data": None,

                "sql": None,

                "intent":
                    intent,

                "message":
                    str(e),

                "answer":
                    "I could not retrieve "
                    "the business documents."

            }

    # ========================================================
    # SQL
    # ========================================================

    sql = generate_sql(
        question,
        intent
    )

    if not sql:

        return {

            "type":
                "error",

            "data": None,

            "sql": None,

            "intent":
                intent,

            "answer":
                "I could not generate "
                "a database query."

        }

    # ========================================================
    # EXECUTE + REPAIR
    # ========================================================

    result = execute_sql_with_retry(
        question,
        intent,
        sql,
        max_retries=5
    )

    # ========================================================
    # FAILED
    # ========================================================

    if not result["success"]:

        print(
            "\n[FINAL SQL ERROR]"
        )

        print(
            result["error"]
        )

        return {

            "type":
                "error",

            "data": None,

            "sql":
                result["sql"],

            "intent":
                intent,

            "attempt":
                result["attempt"],

            "message":
                result["error"],

            "answer":
                "I could not execute "
                "the database query."

        }

    # ========================================================
    # SUCCESS
    # ========================================================

    data = result["data"]

    answer = (
        format_business_answer(
            question,
            intent,
            data
        )
    )

    return {

        "type":
            "sql",

        "data":
            data,

        "sql":
            result["sql"],

        "attempt":
            result["attempt"],

        "intent":
            intent,

        "answer":
            answer

    }


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n=============================================="
    )

    print(
        "AI BUSINESS ASSISTANT ROUTER TEST"
    )

    print(
        "=============================================="
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
