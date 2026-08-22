import ollama


def ask_llm(question: str) -> str:
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response["message"]["content"]