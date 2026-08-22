import os
import re
import chromadb


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# =========================================================
# SCHEMA FILE
# =========================================================

SCHEMA_FILE = os.path.join(
    BASE_DIR,
    "database",
    "schema.sql"
)


# =========================================================
# CHROMADB PATH
# =========================================================

DB_PATH = os.path.join(
    BASE_DIR,
    "rag",
    "project_docs_db"
)


# =========================================================
# CHROMADB
# =========================================================

client = chromadb.PersistentClient(
    path=DB_PATH
)

collection = client.get_or_create_collection(
    name="project_documents"
)


# =========================================================
# READ SCHEMA
# =========================================================

def read_schema():

    if not os.path.exists(SCHEMA_FILE):

        raise FileNotFoundError(
            f"schema.sql not found: {SCHEMA_FILE}"
        )

    with open(
        SCHEMA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        content = file.read()

    if not content.strip():

        raise ValueError(
            "schema.sql is empty."
        )

    return content


# =========================================================
# EXTRACT TABLE DEFINITION
# =========================================================

def get_table_definition(table_name: str):

    content = read_schema()

    # Match:
    #
    # CREATE TABLE products (
    #     ...
    # );
    #
    pattern = (
        r"CREATE\s+TABLE\s+"
        + re.escape(table_name)
        + r"\s*\(.*?\);"
    )

    match = re.search(
        pattern,
        content,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:

        return match.group(0)

    return None


# =========================================================
# GET ALL TABLE NAMES
# =========================================================

def get_schema_tables():

    content = read_schema()

    matches = re.findall(
        r"CREATE\s+TABLE\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        content,
        flags=re.IGNORECASE
    )

    return matches


# =========================================================
# SEARCH PROJECT DOCUMENTS
# =========================================================

def search_project_documents(
    question,
    n_results=5
):

    return collection.query(
        query_texts=[question],
        n_results=n_results
    )


# =========================================================
# INGEST SCHEMA
# =========================================================

def ingest_schema():

    content = read_schema()

    # -----------------------------------------------------
    # Remove old schema chunks
    # -----------------------------------------------------

    existing = collection.get()

    existing_ids = existing.get(
        "ids",
        []
    )

    schema_ids = [
        item
        for item in existing_ids
        if item.startswith("schema_sql_")
    ]

    if schema_ids:

        collection.delete(
            ids=schema_ids
        )

    # -----------------------------------------------------
    # Split schema into logical sections
    # -----------------------------------------------------
    #
    # Instead of blindly splitting every 4000 characters,
    # we try to keep CREATE TABLE definitions together.
    #

    table_pattern = re.compile(
        r"CREATE\s+TABLE\s+"
        r"[a-zA-Z_][a-zA-Z0-9_]*"
        r"\s*\(.*?\);",
        flags=re.IGNORECASE | re.DOTALL
    )

    matches = list(
        table_pattern.finditer(content)
    )

    documents = []
    ids = []
    metadatas = []

    # -----------------------------------------------------
    # Add each table definition as a document
    # -----------------------------------------------------

    for index, match in enumerate(matches):

        table_sql = match.group(0).strip()

        table_match = re.search(
            r"CREATE\s+TABLE\s+"
            r"([a-zA-Z_][a-zA-Z0-9_]*)",
            table_sql,
            flags=re.IGNORECASE
        )

        if table_match:

            table_name = table_match.group(1)

        else:

            table_name = f"unknown_{index}"

        documents.append(
            table_sql
        )

        ids.append(
            f"schema_sql_{table_name}"
        )

        metadatas.append({
            "source": "schema.sql",
            "type": "database_schema",
            "table": table_name
        })

    # -----------------------------------------------------
    # If CREATE TABLE parsing failed
    # -----------------------------------------------------

    if not documents:

        chunk_size = 4000

        chunks = [
            content[i:i + chunk_size]
            for i in range(
                0,
                len(content),
                chunk_size
            )
        ]

        for index, chunk in enumerate(chunks):

            documents.append(chunk)

            ids.append(
                f"schema_sql_chunk_{index}"
            )

            metadatas.append({
                "source": "schema.sql",
                "type": "database_schema",
                "chunk": str(index)
            })

    # -----------------------------------------------------
    # Store in ChromaDB
    # -----------------------------------------------------

    collection.upsert(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )

    return len(documents)


# =========================================================
# DOCUMENT COUNT
# =========================================================

def get_project_document_count():

    return collection.count()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    count = ingest_schema()

    print(
        "✓ schema.sql indexed successfully."
    )

    print(
        f"✓ Documents added: {count}"
    )

    print(
        "✓ Tables found:"
    )

    for table in get_schema_tables():

        print(
            f"  - {table}"
        )

    print(
        f"✓ Total project documents: "
        f"{get_project_document_count()}"
    )