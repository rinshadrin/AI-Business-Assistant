from rag.vector_store import search_documents


query = input("Ask a business question: ")

results = search_documents(
    query,
    n_results=5
)

print("\nRetrieved documents:\n")

for i, document in enumerate(results["documents"][0], 1):
    print(f"{i}. {document}")
    print("-" * 60)