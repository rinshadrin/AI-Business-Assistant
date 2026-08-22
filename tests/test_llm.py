import sys
import os

# Add project root to Python path
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from LLM.model import ask_llm


question = "What is an AI Business Intelligence Assistant?"

answer = ask_llm(question)

print("\n==============================")
print("LLM RESPONSE")
print("==============================\n")
print(answer)