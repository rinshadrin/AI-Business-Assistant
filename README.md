# 🤖 AI Business Assistant for ERP

### LLM + RAG + Text-to-SQL Powered Business Intelligence System

An AI-powered Business Assistant designed for ERP systems that allows users to interact with structured business data using natural language.

Instead of requiring users to manually write SQL queries or navigate through multiple ERP modules, the system provides an intelligent conversational interface for asking business questions.

The application combines:

* 🧠 Large Language Models (LLMs)
* 🔎 Retrieval-Augmented Generation (RAG)
* 🔄 Text-to-SQL
* 🗄️ MySQL
* ⚡ FastAPI
* 💻 Streamlit
* 🧩 SQLAlchemy
* 📚 ChromaDB

to create a natural-language interface over ERP data.

---

## 📌 Table of Contents

* [Project Overview](#-project-overview)
* [Problem Statement](#-problem-statement)
* [Project Objectives](#-project-objectives)
* [Key Features](#-key-features)
* [System Architecture](#-system-architecture)
* [End-to-End Workflow](#-end-to-end-workflow)
* [LLM Layer](#-llm-layer)
* [RAG Pipeline](#-rag-pipeline)
* [Text-to-SQL](#-text-to-sql)
* [Database Layer](#-database-layer)
* [Backend Architecture](#-backend-architecture)
* [Frontend](#-frontend)
* [Project Structure](#-project-structure)
* [Technology Stack](#-technology-stack)
* [Environment Configuration](#-environment-configuration)
* [Installation](#-installation)
* [Database Setup](#-database-setup)
* [Running the Application](#-running-the-application)
* [Testing](#-testing)
* [Security](#-security)
* [Example Questions](#-example-business-questions)
* [Advantages](#-advantages)
* [Limitations](#-current-limitations)
* [Future Enhancements](#-future-enhancements)
* [Project Status](#-project-status)
* [Author](#-author)

---

# 📖 Project Overview

The **AI Business Assistant** acts as an intelligent interface between a business user and an ERP database.

A user can ask a question such as:

```text
What are our top-selling products?
```

Instead of manually writing SQL, the system processes the question and determines how it should be answered.

The general architecture is:

```text
User
 │
 ▼
Natural Language Question
 │
 ▼
Question Router
 │
 ├───────────────┐
 ▼               ▼
SQL Route       RAG Route
 │               │
 ▼               ▼
ERP Database   Business / Schema Context
 │               │
 └───────┬───────┘
         ▼
        LLM
         │
         ▼
Business-Friendly Answer
```

The project is designed around the idea that business users should be able to interact with structured ERP information without needing advanced SQL knowledge.

---

# ❗ Problem Statement

Traditional ERP systems often require users to:

* Navigate multiple modules
* Understand database structures
* Know table relationships
* Understand business terminology
* Write SQL queries for custom analysis
* Manually interpret database results

This creates a barrier for non-technical users.

The goal of this project is to provide a conversational AI layer over the ERP database.

Instead of:

```sql
SELECT ...
FROM ...
JOIN ...
WHERE ...
```

the user can simply ask:

```text
Show me the customers with the highest purchases.
```

The AI system handles the underlying database interaction.

---

# 🎯 Project Objectives

The major objectives are:

1. Enable natural-language interaction with ERP data.
2. Convert business questions into appropriate SQL queries.
3. Retrieve relevant database schema information using RAG.
4. Connect AI-generated queries with a MySQL database.
5. Generate understandable business responses.
6. Separate structured-data questions from document/context questions.
7. Reduce dependency on manual SQL knowledge.
8. Provide a modular architecture that can be extended into a production ERP assistant.

---

# ✨ Key Features

## 🧠 Natural Language Interaction

Users can ask business questions using normal language.

Example:

```text
How many customers do we have?
```

---

## 🔄 Text-to-SQL

The system is designed to translate natural-language questions into SQL queries.

Example:

```text
User:
Show the top 5 products by sales.
```

The AI can generate a database query appropriate for the available schema.

---

## 🔎 Retrieval-Augmented Generation

The RAG pipeline retrieves relevant database schema information before the AI generates or reasons about database queries.

This helps the model understand:

* Available tables
* Available columns
* Table structures
* Explicit relationships
* Database context

---

## 🗄️ MySQL Integration

The system uses MySQL as the structured ERP database.

Database access is handled through SQLAlchemy and PyMySQL.

---

## ⚡ FastAPI Backend

FastAPI provides the backend API layer responsible for connecting the application components.

The backend contains modules for:

* Database connection
* Models
* Schemas
* CRUD operations
* Business queries
* AI services
* Routing

---

## 💻 Streamlit Interface

Streamlit provides a simple conversational interface through which users can interact with the Business Assistant.

---

## 📚 ChromaDB Vector Store

ChromaDB is used to store and retrieve embedded project/schema documents for the RAG pipeline.

---

## 🔐 Environment-Based Configuration

Sensitive database configuration is loaded using environment variables rather than being hard-coded directly into the application.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │        USER          │
                         │ Natural Language     │
                         │      Question        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Question Router    │
                         └──────────┬───────────┘
                                    │
                      ┌─────────────┴─────────────┐
                      │                           │
                      ▼                           ▼
              ┌──────────────┐           ┌──────────────┐
              │   SQL Route  │           │   RAG Route  │
              └──────┬───────┘           └──────┬───────┘
                     │                          │
                     ▼                          ▼
             ┌──────────────┐          ┌────────────────┐
             │ Text-to-SQL  │          │ ChromaDB / RAG │
             └──────┬───────┘          └───────┬────────┘
                    │                           │
                    ▼                           ▼
             ┌──────────────┐          ┌────────────────┐
             │    MySQL     │          │ Schema Context │
             │ ERP Database │          └───────┬────────┘
             └──────┬───────┘                  │
                    │                          │
                    └──────────┬───────────────┘
                               ▼
                       ┌───────────────┐
                       │      LLM      │
                       │ Answer Engine │
                       └───────┬───────┘
                               │
                               ▼
                       ┌───────────────┐
                       │ Final Business│
                       │    Answer     │
                       └───────────────┘
```

---

# 🔄 End-to-End Workflow

The main business-question workflow is implemented around the following sequence:

```text
1. User enters a question
             ↓
2. Question is cleaned and validated
             ↓
3. Router determines the question type
             ↓
       ┌─────┴─────┐
       ↓           ↓
     SQL           RAG
       ↓           ↓
 Database       Retrieve
 Query          Context
       ↓           ↓
       └─────┬─────┘
             ↓
       LLM Processing
             ↓
      Final Answer
```

---

# 🧠 LLM Layer

The LLM layer is responsible for language understanding and answer generation.

The project contains:

```text
LLM/
├── model.py
└── prompts.py
```

### `LLM/model.py`

Provides the LLM interaction layer used by the application.

### `LLM/prompts.py`

Contains prompt-related logic used to guide the model.

The prompts are designed to constrain the model and reduce unsupported answers.

---

# 🔎 RAG Pipeline

The Retrieval-Augmented Generation system provides relevant schema context to the AI.

The RAG implementation contains:

```text
rag/
├── ingest.py
├── project_docs.py
├── rag_pipeline.py
├── vector_store.py
└── test_retrieval.py
```

---

## 1. Schema Ingestion

The ingestion process reads the database schema from:

```text
database/schema.sql
```

The schema is parsed into logical table-level documents where possible.

Each document contains metadata describing its source and table.

---

## 2. Vector Storage

The processed documents are stored in ChromaDB.

The vector store provides functions for:

* Adding documents
* Updating documents
* Searching documents
* Filtering by document type
* Counting stored documents

---

## 3. Retrieval

When a user asks a question, the system retrieves relevant schema information.

For example:

```text
User Question:
Which products generated the highest sales?
```

The RAG layer can retrieve relevant information about tables and columns related to products and sales.

---

## 4. Schema-Aware Reasoning

The RAG prompt instructs the model to use only the retrieved schema information.

It specifically prevents the model from inventing:

* Tables
* Columns
* Foreign-key relationships

Relationships are expected to be used only when they are explicitly available in the schema context.

---

# 🔄 Text-to-SQL

Text-to-SQL is one of the central components of the project.

The purpose is to convert:

```text
Natural Language
        ↓
SQL Query
```

For example:

```text
Show me the top 5 products by sales.
```

can be translated into a SQL query appropriate for the database schema.

The general process is:

```text
User Question
      ↓
Schema Retrieval
      ↓
Relevant Tables
      ↓
Relevant Columns
      ↓
SQL Generation
      ↓
SQL Execution
      ↓
Database Result
      ↓
Natural Language Answer
```

The generated SQL should be based on the available database structure rather than invented tables or fields.

---

# 🗄️ Database Layer

The project uses **MySQL** as the ERP database.

Database-related files include:

```text
database/
└── schema.sql
```

and:

```text
backend/
├── config.py
├── db.py
├── models.py
├── schemas.py
├── crud.py
└── business_queries.py
```

---

## Database Configuration

The database configuration is loaded through environment variables.

Example:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_database_password
DB_NAME=ai_business_assistant
```

This keeps credentials outside the source code.

---

# ⚡ Backend Architecture

The backend is implemented using FastAPI.

```text
backend/
├── __init__.py
├── ai_service.py
├── app.py
├── business_queries.py
├── config.py
├── crud.py
├── db.py
├── main.py
├── models.py
├── router.py
├── schemas.py
└── seed_data.py
```

---

## `config.py`

Loads database configuration from environment variables.

---

## `db.py`

Responsible for database connectivity and database session handling.

---

## `models.py`

Contains SQLAlchemy database models representing ERP entities.

---

## `schemas.py`

Contains Pydantic schemas used for structured API data validation.

---

## `crud.py`

Contains database CRUD operations.

CRUD refers to:

```text
Create
Read
Update
Delete
```

---

## `business_queries.py`

Contains business-oriented database query functionality.

---

## `router.py`

Acts as an important routing layer for determining how a business question should be processed.

The question can be routed toward:

```text
SQL
```

or:

```text
RAG
```

---

## `ai_service.py`

This is one of the main orchestration components.

It connects:

```text
Router
   ↓
SQL / RAG
   ↓
Database / Retrieved Context
   ↓
LLM
   ↓
Final Answer
```

It also contains separate result-formatting logic for SQL results and RAG results.

The SQL result formatter is designed to preserve database values and prevent the LLM from inventing or modifying returned business data.

---

# 💻 Frontend

The project uses **Streamlit** for the user-facing interface.

```text
frontend/
└── app.py
```

The frontend provides the interaction layer through which users can submit business questions and receive AI-generated responses.

---

# 📁 Project Structure

```text
AI-Business-Assistant/
│
├── LLM/
│   ├── model.py
│   └── prompts.py
│
├── backend/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── app.py
│   ├── business_queries.py
│   ├── config.py
│   ├── crud.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── router.py
│   ├── schemas.py
│   └── seed_data.py
│
├── database/
│   └── schema.sql
│
├── frontend/
│   └── app.py
│
├── rag/
│   ├── ingest.py
│   ├── project_docs.py
│   ├── rag_pipeline.py
│   ├── test_retrieval.py
│   └── vector_store.py
│
├── tests/
│   └── test_llm.py
│
├── chat.py
├── text_to_sql.py
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

---

# 🛠️ Technology Stack

| Technology    | Role                           |
| ------------- | ------------------------------ |
| Python        | Core development               |
| FastAPI       | Backend API                    |
| Streamlit     | Frontend                       |
| MySQL         | ERP database                   |
| SQLAlchemy    | ORM/database interaction       |
| PyMySQL       | MySQL driver                   |
| Pydantic      | Data validation                |
| LLM           | Natural-language understanding |
| RAG           | Context retrieval              |
| ChromaDB      | Vector storage                 |
| Pandas        | Data processing                |
| Python-dotenv | Environment configuration      |
| Faker         | Test/seed data generation      |

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/rinshadrin/AI-Business-Assistant.git
cd AI-Business-Assistant
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Configuration

Create a local `.env` file in the project root.

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_database_password
DB_NAME=ai_business_assistant
```

The `.env` file should **never be committed to GitHub**.

Use:

```text
.env.example
```

as the configuration template.

---

# 🗄️ Database Setup

## Step 1 — Install MySQL

Install and start MySQL on your system.

## Step 2 — Create the Database

Create the required database:

```sql
CREATE DATABASE ai_business_assistant;
```

## Step 3 — Create Tables

Execute:

```text
database/schema.sql
```

This creates the database schema required by the application.

## Step 4 — Configure Credentials

Update your local `.env` file.

---

# ▶️ Running the Application

## Start FastAPI

From the project root:

```bash
uvicorn backend.main:app --reload
```

The FastAPI development server will start locally.

---

## Start Streamlit

Open another terminal:

```bash
streamlit run frontend/app.py
```

The Streamlit interface will open in your browser.

---

# 🔎 RAG Setup

Before using schema-based retrieval, the database schema should be indexed.

The RAG ingestion process reads:

```text
database/schema.sql
```

and stores relevant schema information in ChromaDB.

The generated vector database is intentionally excluded from GitHub.

---

# 🧪 Testing

The project includes testing components for LLM and retrieval functionality.

Run the test suite with:

```bash
pytest
```

Individual components can also be tested during development.

For example, the RAG retrieval test can be used to inspect retrieved schema documents.

---

# 💬 Example Business Questions

The assistant is designed for questions such as:

### Customer Questions

```text
How many customers do we have?
```

```text
Show me our customers.
```

### Product Questions

```text
What are the available products?
```

```text
Which products are the most expensive?
```

### Sales Questions

```text
What are the top-selling products?
```

```text
Show the highest sales.
```

### Business Analysis

```text
Which products have the highest sales?
```

```text
Give me information about the products and their sales.
```

The exact questions supported depend on the available ERP schema and implemented query logic.

---

# 🛡️ Security

Security is an important consideration because the application works with database information.

The repository is configured to exclude sensitive and generated files.

The `.gitignore` excludes items such as:

```text
.env
venv/
__pycache__/
*.pyc
rag/chroma_db/
rag/project_docs_db/
```

### Never commit:

* Database passwords
* API keys
* Authentication tokens
* Private credentials
* Local `.env` files
* Virtual environments
* Generated vector databases

---

# 🧠 AI Safety Considerations

The project includes prompt-level restrictions intended to reduce hallucinations.

For SQL results, the response generation logic instructs the model to:

* Use only returned database information
* Preserve database values
* Avoid inventing records
* Avoid modifying numbers
* Avoid removing returned records
* Respect database ordering
* Avoid inventing business facts

For schema retrieval, the RAG prompt instructs the model to:

* Use only retrieved schema information
* Avoid inventing tables
* Avoid inventing columns
* Avoid inventing foreign-key relationships
* Use relationships only when explicitly available

These controls improve reliability, although they do not replace production-grade SQL validation, authorization, and database security.

---

# 📊 Advantages

### For Business Users

* No SQL knowledge required
* Natural-language interaction
* Faster access to business information
* Easier exploration of ERP data

### For Developers

* Modular architecture
* Separate AI, database, RAG, backend, and frontend layers
* Extensible design
* Environment-based configuration

### For ERP Systems

The architecture can potentially be extended to support additional business modules and more complex analytical workflows.

---

# ⚠️ Current Limitations

This project is currently a development/portfolio implementation.

Potential production requirements include:

* Strong SQL validation
* Read-only database permissions for AI-generated queries
* Authentication
* Role-based access control
* Query timeout and resource limits
* Comprehensive automated testing
* Production-grade logging
* Monitoring
* Rate limiting
* Better error handling
* Secure deployment infrastructure

These should be addressed before connecting the system to sensitive production ERP data.

---

# 🚀 Future Enhancements

## 🔐 Security

* User authentication
* Role-based access control
* Permission-aware database access
* Read-only SQL execution
* SQL query validation
* Query safety checks

## 📊 Analytics

* Automated dashboards
* Business KPI generation
* Sales trend analysis
* Customer analytics
* Product performance analytics
* Interactive charts

## 🧠 AI

* Improved Text-to-SQL accuracy
* Schema-aware query planning
* Query explanation
* SQL correction and retry
* Better conversational memory
* Multi-step business reasoning

## 🏢 ERP Integration

Potential modules include:

```text
Products
Customers
Suppliers
Employees
Sales
Inventory
Purchasing
Finance
```

## ☁️ Deployment

Future production deployment could include:

```text
Docker
        ↓
FastAPI
        ↓
MySQL
        ↓
Vector Database
        ↓
Cloud Infrastructure
```

---

# 🔮 Vision

The long-term goal is to evolve the project into an intelligent ERP assistant where business users can interact with organizational data through a conversational interface.

Instead of asking:

```text
Which table contains customer information?
```

or writing:

```sql
SELECT ...
```

users can simply ask:

```text
Show me our best customers this year.
```

and receive a useful business response.

---

# 📈 Project Workflow Summary

```text
                 USER
                  │
                  ▼
        Natural Language Question
                  │
                  ▼
           Question Router
                  │
          ┌───────┴───────┐
          │               │
          ▼               ▼
       SQL Query        RAG Query
          │               │
          ▼               ▼
    Schema Context    ChromaDB
          │               │
          ▼               ▼
       Text-to-SQL    Retrieved Context
          │               │
          ▼               │
       MySQL              │
          │               │
          └───────┬───────┘
                  ▼
                 LLM
                  │
                  ▼
        Business-Friendly Answer
                  │
                  ▼
                 USER
```


# 👨‍💻 Author

## Rinshad

**Data Science & Artificial Intelligence**

GitHub:

https://github.com/rinshadrin

---

## ⭐ If you find this project interesting

Feel free to explore the repository, review the architecture, and follow the development of the AI Business Assistant.
