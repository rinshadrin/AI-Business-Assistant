from sqlalchemy import text
from backend.db import SessionLocal
from backend.models import Base
from LLM.model import ask_llm
from rag.rag_pipeline import retrieve_context
import re


# =========================================================
# DATABASE SCHEMA
# =========================================================

def get_database_schema():
    """
    Automatically read the database schema from SQLAlchemy.
    """

    schema = []

    for table in Base.metadata.sorted_tables:

        columns = []

        for column in table.columns:

            info = f"{column.name} {column.type}"

            if column.primary_key:
                info += " PRIMARY KEY"

            for fk in column.foreign_keys:
                info += f" REFERENCES {fk.target_fullname}"

            columns.append(info)

        schema.append(
            f"TABLE {table.name}:\n"
            + "\n".join(
                f"  - {column}"
                for column in columns
            )
        )

    return "\n\n".join(schema)


# =========================================================
# QUESTION CLASSIFICATION
# =========================================================

def classify_question(question: str):

    prompt = f"""
You are a business AI question classifier.

Classify the question into exactly ONE:

sql
rag

Use SQL when the question requires actual data from
the ERP database.

Examples:

- products
- prices
- stock
- low stock
- reorder
- customers
- suppliers
- employees
- orders
- payments
- sales
- revenue
- profit
- loss
- counts
- totals
- averages
- highest
- lowest
- most
- least
- comparisons
- database records

Use RAG when the question asks about:

- company policies
- procedures
- rules
- documentation
- business guidelines
- general information stored in documents

IMPORTANT:

Any question asking for actual ERP business data
must use SQL.

User question:
{question}

Return ONLY:

sql

or

rag
"""

    result = ask_llm(prompt).strip().lower()

    if "sql" in result:
        return "sql"

    if "rag" in result:
        return "rag"

    return "sql"


# =========================================================
# CLEAN SQL
# =========================================================

def clean_sql(sql: str):

    sql = sql.strip()

    # Remove markdown
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

    # Remove common LLM explanation before SELECT
    match = re.search(
        r"\bSELECT\b.*",
        sql,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:
        sql = match.group(0).strip()

    # Remove explanation after semicolon
    if ";" in sql:
        sql = sql.split(";")[0]

    sql = sql.rstrip(";").strip()

    return sql


# =========================================================
# SQL SAFETY
# =========================================================

def validate_sql(sql: str):

    sql_upper = sql.upper().strip()

    if not sql_upper.startswith("SELECT"):

        return (
            False,
            "Only SELECT queries are allowed."
        )

    forbidden_keywords = [
        "INSERT ",
        "UPDATE ",
        "DELETE ",
        "DROP ",
        "ALTER ",
        "CREATE ",
        "TRUNCATE ",
        "REPLACE ",
        "GRANT ",
        "REVOKE ",
        "EXEC ",
        "EXECUTE ",
        "CALL "
    ]

    for keyword in forbidden_keywords:

        if keyword in sql_upper:

            return (
                False,
                f"Unsafe SQL operation detected: "
                f"{keyword.strip()}"
            )

    return True, None


# =========================================================
# SQL GENERATOR
# =========================================================

def generate_sql(question: str):

    schema = get_database_schema()

    prompt = f"""
You are an expert MySQL SQL generator for an ERP
Business Intelligence Assistant.

Your job is to convert the user's natural-language
question into ONE correct MySQL SELECT query.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}


=========================================================
GENERAL RULES
=========================================================

1. Use ONLY tables and columns that exist in the schema.

2. NEVER invent table names.

3. NEVER invent column names.

4. Every column must belong to an existing table.

5. Verify every JOIN using the actual foreign keys.

6. Use the simplest query that correctly answers
   the question.

7. Do not add unnecessary JOINs.

8. SELECT queries ONLY.

9. Never INSERT, UPDATE, DELETE, DROP, ALTER or CREATE.

10. Return ONLY SQL.

11. Do not return explanations.

12. Do not return markdown.

13. Do not write "Here is the query".

14. Do not write anything before or after the SQL.


=========================================================
PRODUCT QUESTIONS
=========================================================

Most expensive product:

SELECT product_name, unit_price
FROM products
ORDER BY unit_price DESC
LIMIT 1


Cheapest product:

SELECT product_name, unit_price
FROM products
ORDER BY unit_price ASC
LIMIT 1


Available products:

SELECT product_name, unit_price, stock_quantity
FROM products


=========================================================
LOW STOCK
=========================================================

"Which products have low stock?"

ALWAYS interpret low stock as:

stock_quantity <= reorder_level

Use:

SELECT
    product_name,
    stock_quantity,
    reorder_level
FROM products
WHERE stock_quantity <= reorder_level


Do NOT use:

stock_quantity < 1

Do NOT multiply reorder_level.

Do NOT invent another stock rule.


=========================================================
REORDER QUESTIONS
=========================================================

"Which products need to be reordered?"

Use:

SELECT
    product_name,
    stock_quantity,
    reorder_level
FROM products
WHERE stock_quantity <= reorder_level


=========================================================
COUNT QUESTIONS
=========================================================

"How many customers?"

Use:

SELECT COUNT(*) AS total_customers
FROM customers


"How many orders?"

Use:

SELECT COUNT(*) AS total_orders
FROM orders


"How many products?"

Use:

SELECT COUNT(*) AS total_products
FROM products


Use COUNT(*) for simple row counts.


=========================================================
SUPPLIER QUESTIONS
=========================================================

"Which supplier supplies the most products?"

Use:

SELECT
    s.supplier_name,
    COUNT(p.product_id) AS product_count
FROM suppliers s
JOIN products p
    ON s.supplier_id = p.supplier_id
GROUP BY
    s.supplier_id,
    s.supplier_name
ORDER BY product_count DESC
LIMIT 1


If the user asks for ALL suppliers ranked by
number of products, remove LIMIT 1.


=========================================================
CATEGORY QUESTIONS
=========================================================

"Which category has the most products?"

Use:

SELECT
    c.category_name,
    COUNT(p.product_id) AS product_count
FROM categories c
JOIN products p
    ON c.category_id = p.category_id
GROUP BY
    c.category_id,
    c.category_name
ORDER BY product_count DESC
LIMIT 1


=========================================================
TOTAL SALES
=========================================================

IMPORTANT:

In this ERP database, the orders table contains:

orders.total_amount

Therefore, when the user asks:

"What are our total sales?"

"How much sales did we make?"

"What is our total revenue from orders?"

Use the order totals.

Correct query:

SELECT
    COALESCE(SUM(total_amount), 0) AS total_sales
FROM orders


DO NOT calculate sales using:

order_items.quantity * products.unit_price

unless the user explicitly asks for
item-level sales calculation.

DO NOT JOIN order_items for a normal
"total sales" question.


=========================================================
PROFIT / LOSS
=========================================================

IMPORTANT:

For this ERP database, profit is:

TOTAL SALES / ORDER REVENUE
minus
TOTAL PURCHASE COST


Sales come from:

orders.total_amount


Purchase cost comes from:

purchase_orders.total_amount


Therefore:

PROFIT = SUM(orders.total_amount)
         -
         SUM(purchase_orders.total_amount)


For:

"Are we making a profit or a loss?"

Use:

SELECT
    COALESCE(
        (SELECT SUM(total_amount)
         FROM orders),
        0
    )
    -
    COALESCE(
        (SELECT SUM(total_amount)
         FROM purchase_orders),
        0
    ) AS profit


Do NOT use:

purchase_items.quantity * order_items.unit_price

Do NOT join purchase_items to order_items.

Do NOT match purchases to orders by product.

Do NOT invent purchase columns.

Do NOT calculate cost using unrelated tables.

The purchase_orders table already contains:

purchase_orders.total_amount


=========================================================
PROFIT / LOSS WITH STATUS
=========================================================

If the user asks:

"Are we making a profit or loss?"

Return the calculated difference.

If profit > 0:

Profit

If profit < 0:

Loss

If profit = 0:

Break-even


The SQL should calculate the numeric profit value.


=========================================================
ORDER QUESTIONS
=========================================================

For:

"How many orders?"

Use:

SELECT COUNT(*) AS total_orders
FROM orders


For:

"Show me orders"

Use columns from orders.

For customer information, JOIN:

orders.customer_id = customers.customer_id


=========================================================
PAYMENT QUESTIONS
=========================================================

Payments are related to orders through:

payments.order_id = orders.order_id


For total payments:

SELECT
    COALESCE(SUM(amount), 0) AS total_payments
FROM payments


For payment information, use the payments table.


=========================================================
INVENTORY QUESTIONS
=========================================================

Inventory transactions are related to products through:

inventory_transactions.product_id =
products.product_id


Use inventory_transactions for transaction history.

Use products.stock_quantity for current stock.


=========================================================
PURCHASE QUESTIONS
=========================================================

Purchase orders are related to suppliers through:

purchase_orders.supplier_id =
suppliers.supplier_id


Purchase items are related to purchase orders through:

purchase_items.purchase_order_id =
purchase_orders.purchase_order_id


Purchase items are related to products through:

purchase_items.product_id =
products.product_id


For total purchase cost, prefer:

purchase_orders.total_amount

Do NOT reconstruct the purchase total unless
the question specifically asks for item-level
calculation.


=========================================================
IMPORTANT JOIN RULE
=========================================================

Only use relationships that actually exist.

VALID examples:

orders.customer_id
→ customers.customer_id

order_items.order_id
→ orders.order_id

order_items.product_id
→ products.product_id

products.category_id
→ categories.category_id

products.supplier_id
→ suppliers.supplier_id

purchase_orders.supplier_id
→ suppliers.supplier_id

purchase_items.purchase_order_id
→ purchase_orders.purchase_order_id

purchase_items.product_id
→ products.product_id

payments.order_id
→ orders.order_id

inventory_transactions.product_id
→ products.product_id


NEVER create relationships that do not exist.


=========================================================
QUESTION INTERPRETATION
=========================================================

"Most expensive product"

means highest products.unit_price.

"Most products supplied by supplier"

means COUNT(products.product_id)
GROUP BY supplier.

"Low stock"

means:

stock_quantity <= reorder_level

"Total sales"

means:

SUM(orders.total_amount)

"Profit or loss"

means:

SUM(orders.total_amount)
-
SUM(purchase_orders.total_amount)


=========================================================
FINAL CHECK
=========================================================

Before returning SQL verify:

1. Every table exists.
2. Every column exists.
3. Every JOIN is valid.
4. No unrelated tables are used.
5. No invented business rules are used.
6. The SQL directly answers the question.
7. The query is SELECT only.
8. No explanation is returned.

Return ONLY the SQL query.
"""

    sql = ask_llm(prompt)

    sql = clean_sql(sql)

    print("[GENERATED SQL]")
    print(sql)

    return sql


# =========================================================
# EXECUTE SQL
# =========================================================

def execute_sql(sql: str):

    valid, error = validate_sql(sql)

    if not valid:

        return {
            "error": "unsafe_sql",
            "message": error
        }

    session = SessionLocal()

    try:

        result = session.execute(
            text(sql)
        )

        rows = result.mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        session.close()


# =========================================================
# REPAIR SQL
# =========================================================

def repair_sql(
    question: str,
    bad_sql: str,
    error_message: str
):

    schema = get_database_schema()

    prompt = f"""
You are repairing a failed MySQL SELECT query.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

FAILED SQL:
{bad_sql}

ERROR:
{error_message}

Generate ONE corrected SELECT query.

Rules:

1. Use only existing tables.
2. Use only existing columns.
3. Verify every JOIN.
4. Do not invent columns.
5. Do not invent tables.
6. Do not add unnecessary JOINs.
7. SELECT only.
8. Return ONLY SQL.
9. No markdown.
10. No explanation.

IMPORTANT BUSINESS RULES:

Total sales =
SUM(orders.total_amount)

Purchase cost =
SUM(purchase_orders.total_amount)

Profit =
SUM(orders.total_amount)
-
SUM(purchase_orders.total_amount)

Low stock =
stock_quantity <= reorder_level

Correct SQL:
"""

    corrected = ask_llm(prompt)

    return clean_sql(corrected)


# =========================================================
# EXECUTE WITH RETRY
# =========================================================

def execute_sql_with_retry(
    question: str,
    sql: str,
    max_retries: int = 2
):

    current_sql = sql
    last_error = None

    for attempt in range(max_retries + 1):

        valid, validation_error = validate_sql(
            current_sql
        )

        if not valid:

            last_error = validation_error

        else:

            try:

                data = execute_sql(
                    current_sql
                )

                if (
                    isinstance(data, dict)
                    and "error" in data
                ):

                    last_error = data.get(
                        "message",
                        "SQL execution failed."
                    )

                else:

                    return {
                        "success": True,
                        "data": data,
                        "sql": current_sql,
                        "attempt": attempt + 1
                    }

            except Exception as e:

                last_error = str(e)

        print(
            f"[SQL RETRY] Attempt {attempt + 1} failed."
        )

        if attempt >= max_retries:
            break

        current_sql = repair_sql(
            question,
            current_sql,
            str(last_error)
        )

    return {
        "success": False,
        "data": None,
        "sql": current_sql,
        "error": str(last_error)
    }


# =========================================================
# MAIN ROUTER
# =========================================================

def route_question(question: str):

    question = question.strip()

    if not question:

        return {
            "type": "unknown",
            "data": None
        }

    try:

        route_type = classify_question(
            question
        )

        print(
            f"[ROUTER] Question type: {route_type}"
        )

        # =================================================
        # SQL
        # =================================================

        if route_type == "sql":

            print(
                "[ROUTER] Generating SQL..."
            )

            sql = generate_sql(
                question
            )

            result = execute_sql_with_retry(
                question,
                sql,
                max_retries=2
            )

            if result["success"]:

                return {
                    "type": "sql",
                    "data": result["data"],
                    "sql": result["sql"],
                    "attempt": result["attempt"]
                }

            return {
                "type": "error",
                "data": None,
                "sql": result["sql"],
                "message": result["error"]
            }

        # =================================================
        # RAG
        # =================================================

        if route_type == "rag":

            context = retrieve_context(
                question,
                n_results=5
            )

            return {
                "type": "rag",
                "data": {
                    "question": question,
                    "context": context
                }
            }

        return {
            "type": "unknown",
            "data": None
        }

    except Exception as e:

        print(
            f"[ROUTER ERROR] {str(e)}"
        )

        return {
            "type": "error",
            "data": None,
            "message": str(e)
        }


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ERP DATABASE AI")
    print("=" * 60)

    while True:

        question = input(
            "\nAsk a database question "
            "(type 'exit' to stop): "
        )

        if question.lower().strip() == "exit":
            break

        result = route_question(
            question
        )

        print("\nResult:\n")
        print(result)