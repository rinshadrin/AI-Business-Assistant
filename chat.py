import sys
import os

# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# =========================================================
# IMPORTS
# =========================================================

from LLM.model import ask_llm
from backend.ai_service import answer_business_question
from rag.vector_store import get_document_count


# =========================================================
# COLORS
# =========================================================

RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
WHITE = "\033[97m"


# =========================================================
# STARTUP CHECKS
# =========================================================

def check_ollama():

    try:

        # Simple LLM test
        response = ask_llm("Reply with exactly: OK")

        if response:

            print(
                f"{GREEN}✓ Ollama connected{RESET}"
            )

            print(
                f"{GREEN}✓ Model: llama3.2{RESET}"
            )

            return True

        print(
            f"{RED}✗ Ollama returned an empty response{RESET}"
        )

        return False

    except Exception as e:

        print(
            f"{RED}✗ Ollama connection failed{RESET}"
        )

        print(
            f"{RED}  {e}{RESET}"
        )

        return False


def check_rag():

    try:

        count = get_document_count()

        print(
            f"{GREEN}✓ ChromaDB connected{RESET}"
        )

        print(
            f"{GREEN}✓ Documents indexed: {count}{RESET}"
        )

        return True

    except Exception as e:

        print(
            f"{RED}✗ ChromaDB connection failed{RESET}"
        )

        print(
            f"{RED}  {e}{RESET}"
        )

        return False


def check_pipeline():

    try:

        # Test the complete AI pipeline
        answer = answer_business_question(
            "How many products do we have?"
        )

        if answer:

            print(
                f"{GREEN}✓ AI Business Intelligence pipeline ready{RESET}"
            )

            return True

        print(
            f"{RED}✗ AI pipeline returned empty response{RESET}"
        )

        return False

    except Exception as e:

        print(
            f"{RED}✗ AI pipeline check failed{RESET}"
        )

        print(
            f"{RED}  {e}{RESET}"
        )

        return False


# =========================================================
# STARTUP SCREEN
# =========================================================

def startup():

    print()
    print(
        f"{CYAN}"
        "============================================================"
        f"{RESET}"
    )

    print(
        f"{CYAN}        AI BUSINESS ASSISTANT - TERMINAL MODE{RESET}"
    )

    print(
        f"{CYAN}"
        "============================================================"
        f"{RESET}"
    )

    print()

    print(f"{WHITE}Checking system components...{RESET}")
    print()

    ollama_ok = check_ollama()

    rag_ok = check_rag()

    pipeline_ok = check_pipeline()

    print()

    print(
        f"{CYAN}"
        "------------------------------------------------------------"
        f"{RESET}"
    )

    if ollama_ok and rag_ok and pipeline_ok:

        print(
            f"{GREEN}✓ ALL SYSTEMS READY{RESET}"
        )

        print(
            f"{GREEN}✓ Ollama + LLM + RAG + SQL pipeline active{RESET}"
        )

    else:

        print(
            f"{YELLOW}⚠ Some components are not ready.{RESET}"
        )

        print(
            f"{YELLOW}The chat may not work correctly.{RESET}"
        )

    print(
        f"{CYAN}"
        "------------------------------------------------------------"
        f"{RESET}"
    )

    print()

    print(
        f"{YELLOW}"
        "Type 'quit' or 'exit' to close the assistant."
        f"{RESET}"
    )

    print()


# =========================================================
# CHAT LOOP
# =========================================================

def chat():

    startup()

    while True:

        try:

            question = input(
                f"{CYAN}You:{RESET} "
            ).strip()

        except (KeyboardInterrupt, EOFError):

            print()
            print(
                f"{YELLOW}Exiting AI Business Assistant...{RESET}"
            )

            break

        # -------------------------------------------------
        # EMPTY QUESTION
        # -------------------------------------------------

        if not question:

            continue

        # -------------------------------------------------
        # EXIT
        # -------------------------------------------------

        if question.lower() in {
            "quit",
            "exit",
            "q"
        }:

            print()

            print(
                f"{YELLOW}"
                "AI Business Assistant closed."
                f"{RESET}"
            )

            print()

            break

        # -------------------------------------------------
        # PROCESS QUESTION
        # -------------------------------------------------

        print()

        print(
            f"{YELLOW}AI is thinking...{RESET}"
        )

        try:

            answer = answer_business_question(
                question
            )

            print()

            print(
                f"{GREEN}AI:{RESET}"
            )

            print(answer)

        except Exception as e:

            print()

            print(
                f"{RED}AI Error:{RESET}"
            )

            print(e)

        print()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    chat()