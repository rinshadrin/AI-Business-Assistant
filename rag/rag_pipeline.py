from rag.vector_store import search_documents
from LLM.model import ask_llm


# =========================================================
# RETRIEVE DATABASE SCHEMA
# =========================================================

def retrieve_context(question, n_results=10):

    results = search_documents(
        query=question,
        n_results=n_results,
        document_type="schema"
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    if not documents:
        return "No relevant database schema was found."

    # -----------------------------------------------------
    # REMOVE DUPLICATE TABLE DOCUMENTS
    # -----------------------------------------------------

    unique_documents = []
    seen_tables = set()

    for document in documents:

        table_name = None

        for line in document.splitlines():

            if line.startswith("TABLE:"):
                table_name = line.replace(
                    "TABLE:",
                    ""
                ).strip()
                break

        # If table name is available, deduplicate it
        if table_name:

            if table_name in seen_tables:
                continue

            seen_tables.add(table_name)

        unique_documents.append(document)

    # -----------------------------------------------------
    # FORMAT SCHEMA CONTEXT
    # -----------------------------------------------------

    return "\n\n".join(
        unique_documents
    )


# =========================================================
# ASK BUSINESS AI
# =========================================================

def ask_business_ai(question: str):

    context = retrieve_context(
        question,
        n_results=10
    )

    prompt = f"""
You are an ERP database schema assistant.

Your task is to identify the exact database tables,
columns, and foreign-key relationships required to
answer the user's question.

DATABASE SCHEMA:

{context}

USER QUESTION:

{question}

STRICT RULES:

1. Use ONLY information explicitly present in the
   DATABASE SCHEMA.

2. NEVER invent a table.

3. NEVER invent a column.

4. NEVER invent a foreign-key relationship.

5. NEVER infer a relationship just because two columns
   have similar names.

6. A relationship is valid ONLY when it is explicitly
   listed under:
   "FOREIGN KEY RELATIONSHIPS".

7. Do not generate SQL.

8. Do not provide business numbers.

9. Do not guess.

10. If the retrieved schema is insufficient, say:
    "The retrieved database schema is insufficient
    to determine this."

OUTPUT FORMAT:

Relevant tables:
- table_name

Relevant columns:
- table_name.column_name

Explicit relationships:
- table.column → table.column

Reason:
- Briefly explain why these tables and columns
  are relevant.

IMPORTANT:

Only mention relationships that are explicitly written
in the provided schema.
"""

    answer = ask_llm(prompt)

    return answer


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ERP DATABASE SCHEMA RAG TEST")
    print("=" * 60)

    while True:

        question = input(
            "\nAsk a database question "
            "(type 'exit' to stop): "
        )

        if question.lower().strip() == "exit":

            print("\nExiting...")
            break

        if not question.strip():
            continue

        answer = ask_business_ai(
            question
        )

        print("\nAI Answer:\n")
        print(answer)