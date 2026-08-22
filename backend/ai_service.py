
import json

from backend.router import route_question
from LLM.model import ask_llm
from rag.rag_pipeline import retrieve_context


# =========================================================
# SQL RESULT -> LLM ANSWER
# =========================================================

def format_sql_result(question: str, data) -> str:
    """
    Convert exact SQL/database results into a natural-language
    answer.

    IMPORTANT:
    The LLM must preserve ALL records returned by the database.
    It must not invent, remove, filter, or modify database data.
    """

    # -----------------------------------------------------
    # No result
    # -----------------------------------------------------

    if data is None:
        return "No matching business data was found."

    if isinstance(data, list) and len(data) == 0:
        return "No matching business data was found."

    # -----------------------------------------------------
    # Convert database result to JSON
    # -----------------------------------------------------

    try:

        serialized_data = json.dumps(
            data,
            default=str,
            indent=2
        )

    except Exception:

        serialized_data = str(data)

    # -----------------------------------------------------
    # LLM Prompt
    # -----------------------------------------------------

    prompt = f"""
You are an AI Business Assistant.

Answer the user's business question using ONLY the
database result provided below.

USER QUESTION:
{question}

DATABASE RESULT:
{serialized_data}

STRICT RULES:

1. Use ONLY information present in DATABASE RESULT.

2. NEVER invent business facts.

3. NEVER invent products, customers, suppliers,
   categories, prices, quantities, dates, or numbers.

4. NEVER change any value from DATABASE RESULT.

5. NEVER omit any database record.

6. If DATABASE RESULT contains 5 records,
   the final answer MUST include all 5 records.

7. If DATABASE RESULT contains 10 records,
   the final answer MUST include all 10 records.

8. For list questions, preserve the COMPLETE list.

9. Do NOT filter records yourself.

10. Do NOT remove records because you think they
    are unimportant.

11. Do NOT add information that is not present
    in DATABASE RESULT.

12. If the result is empty, say:
    "No matching business data was found."

13. Answer the user's actual question directly.

14. Keep the answer clear and business-friendly.

15. For ranking questions such as:
    - most expensive
    - cheapest
    - highest
    - lowest
    - most products
    - least products

    trust the ordering/calculation already performed
    by the database query.

16. Do not perform a different calculation yourself
    when the database has already provided the result.

17. Preserve exact database numbers.

18. If a product name appears in DATABASE RESULT,
    use that exact product name.

19. If a supplier name appears in DATABASE RESULT,
    use that exact supplier name.

20. If a category name appears in DATABASE RESULT,
    use that exact category name.

21. If multiple records are returned, present them
    as a numbered or bulleted list when appropriate.

22. Do not mention:
    - SQL
    - database query
    - prompt
    - RAG
    - retrieval
    - internal processing
    - LLM

Return ONLY the final business answer.
"""

    # -----------------------------------------------------
    # Ask LLM
    # -----------------------------------------------------

    try:

        answer = ask_llm(prompt)

        return answer.strip()

    except Exception as e:

        print(
            f"[SQL LLM ERROR] {str(e)}"
        )

        # -------------------------------------------------
        # Safe fallback
        # -------------------------------------------------

        if isinstance(data, list):

            lines = []

            for item in data:

                if isinstance(item, dict):

                    parts = []

                    for key, value in item.items():

                        parts.append(
                            f"{key}: {value}"
                        )

                    lines.append(
                        "- " + ", ".join(parts)
                    )

                else:

                    lines.append(
                        f"- {item}"
                    )

            return "\n".join(lines)

        if isinstance(data, dict):

            return "\n".join(
                f"{key}: {value}"
                for key, value in data.items()
            )

        return str(data)


# =========================================================
# RAG RESULT -> LLM ANSWER
# =========================================================

def format_rag_result(
    question: str,
    context: str
) -> str:
    """
    Convert retrieved business-document context into
    a natural-language answer.

    The LLM can only use the retrieved context.
    """

    # -----------------------------------------------------
    # No RAG context
    # -----------------------------------------------------

    if not context or not context.strip():

        return (
            "The available business information is not "
            "sufficient to answer this question."
        )

    # -----------------------------------------------------
    # RAG Prompt
    # -----------------------------------------------------

    prompt = f"""
You are an AI Business Assistant.

Answer the user's question using ONLY the business
information contained in the retrieved context.

USER QUESTION:
{question}

RETRIEVED BUSINESS CONTEXT:
{context}

STRICT RULES:

1. Use ONLY information contained in the context.

2. NEVER invent business facts.

3. NEVER guess missing information.

4. If the context does not contain enough information,
   clearly say that the available business information
   is not sufficient.

5. Do not create policies or rules that are not present
   in the context.

6. Preserve important names, values, rules, and details
   exactly as provided.

7. Answer the user's actual question directly.

8. Keep the answer clear and concise.

9. Do not mention:
   - RAG
   - embeddings
   - vector database
   - retrieval
   - prompt
   - LLM
   - internal processing

Return ONLY the final business answer.
"""

    # -----------------------------------------------------
    # Ask LLM
    # -----------------------------------------------------

    try:

        answer = ask_llm(prompt)

        return answer.strip()

    except Exception as e:

        print(
            f"[RAG LLM ERROR] {str(e)}"
        )

        return (
            "I was unable to generate an answer from "
            "the available business information."
        )


# =========================================================
# MAIN AI BUSINESS QUESTION
# =========================================================

def answer_business_question(
    question: str
) -> str:
    """
    Main AI Business Assistant pipeline.

    Architecture:

        USER QUESTION
              |
              v
        ROUTER / CLASSIFIER
              |
        +-----+-----+
        |           |
       SQL         RAG
        |           |
        v           v
    DATABASE    DOCUMENTS
        |           |
        +-----+-----+
              |
              v
             LLM
              |
              v
        FINAL ANSWER
    """

    # -----------------------------------------------------
    # Clean question
    # -----------------------------------------------------

    question = question.strip()

    # -----------------------------------------------------
    # Empty question
    # -----------------------------------------------------

    if not question:

        return "Please enter a business question."

    try:

        # =================================================
        # ROUTER
        # =================================================

        route = route_question(question)

        if not isinstance(route, dict):

            return (
                "Unable to determine how to answer "
                "the business question."
            )

        route_type = route.get("type")

        # =================================================
        # SQL ROUTE
        # =================================================

        if route_type == "sql":

            data = route.get("data")

            return format_sql_result(
                question,
                data
            )

        # =================================================
        # RAG ROUTE
        # =================================================

        if route_type == "rag":

            # -------------------------------------------------
            # Retrieve business context
            # -------------------------------------------------

            try:

                context = retrieve_context(
                    question,
                    n_results=5
                )

            except Exception as e:

                print(
                    f"[RAG RETRIEVAL ERROR] {str(e)}"
                )

                return (
                    "I was unable to retrieve the relevant "
                    "business information."
                )

            # -------------------------------------------------
            # Generate answer
            # -------------------------------------------------

            return format_rag_result(
                question,
                context
            )

        # =================================================
        # ROUTER ERROR
        # =================================================

        if route_type == "error":

            error_message = route.get(
                "message",
                "Unknown routing error."
            )

            print(
                f"[ROUTER ERROR] {error_message}"
            )

            return (
                "I was unable to process that business "
                "question. Please try again."
            )

        # =================================================
        # UNKNOWN
        # =================================================

        return (
            "I could not determine how to answer "
            "that business question."
        )

    # =====================================================
    # GLOBAL ERROR
    # =====================================================

    except Exception as e:

        print(
            f"[AI SERVICE ERROR] {str(e)}"
        )

        return (
            "Unable to process the business question "
            "at the moment."
        )


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI BUSINESS ASSISTANT")
    print("=" * 60)

    while True:

        question = input(
            "\nAsk a business question "
            "(type 'exit' to stop): "
        )

        if question.lower().strip() == "exit":
            break

        answer = answer_business_question(
            question
        )

        print("\nAI Answer:\n")
        print(answer)
