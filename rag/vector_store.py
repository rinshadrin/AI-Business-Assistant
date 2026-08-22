import chromadb


# =========================================================
# CHROMA DATABASE
# =========================================================

client = chromadb.PersistentClient(
    path="rag/chroma_db"
)


collection = client.get_or_create_collection(
    name="business_knowledge"
)


# =========================================================
# ADD / UPDATE DOCUMENTS
# =========================================================

def add_documents(documents, ids, metadatas=None):

    collection.upsert(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )


# =========================================================
# SEARCH DOCUMENTS
# =========================================================

def search_documents(
    query,
    n_results=5,
    document_type=None
):

    # -----------------------------------------------------
    # NORMAL SEARCH
    # -----------------------------------------------------

    if document_type is None:

        return collection.query(
            query_texts=[query],
            n_results=n_results
        )

    # -----------------------------------------------------
    # FILTERED SEARCH
    # -----------------------------------------------------

    return collection.query(
        query_texts=[query],
        n_results=n_results,
        where={
            "type": document_type
        }
    )


# =========================================================
# DOCUMENT COUNT
# =========================================================

def get_document_count():

    return collection.count()