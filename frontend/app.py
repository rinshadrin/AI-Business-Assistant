import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="🤖",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"


# =========================================================
# API HELPER
# =========================================================

def get_data(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}")

        if response.status_code == 200:
            return response.json()

        return Noneimport streamlit as st
import pandas as pd

from backend.router import route_question


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 AI Business Assistant")

    st.caption(
        "Intelligent assistant for your ERP business data."
    )

    st.divider()

    if st.button(
        "＋ New Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("What I can do")

    st.write(
        """
        **Business Data**

        • Sales analysis  
        • Product information  
        • Customer data  
        • Supplier information  
        • Inventory analysis  
        • Order information  

        **Database**

        • Table information  
        • Database structure  
        • SQL queries  
        • Database results  

        **Business Knowledge**

        • Company policies  
        • Business documents  
        • Internal information
        """
    )

    st.divider()

    st.caption(
        "AI Business Assistant • ERP Intelligence"
    )


# ============================================================
# HEADER
# ============================================================

st.title("🤖 AI Business Assistant")

st.caption(
    "Ask questions about your business data"
)


# ============================================================
# WELCOME SCREEN
# ============================================================

if len(st.session_state.messages) == 0:

    st.write("")
    st.write("")
    st.write("")
    st.write("")

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        st.markdown(
            """
            <div style="
                text-align:center;
                font-size:55px;
                margin-bottom:10px;
            ">
                🤖
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <h2 style="text-align:center;">
                How can I help you today?
            </h2>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <p style="
                text-align:center;
                color:gray;
                font-size:16px;
            ">
                Ask anything about your business data,
                database or business documents.
            </p>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    if message["role"] == "user":

        with st.chat_message("user"):

            st.write(
                message["content"]
            )

    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    else:

        with st.chat_message(
            "assistant",
            avatar="🤖"
        ):

            # ================================================
            # ANSWER
            # ================================================

            st.markdown("### 💬 Answer")

            st.write(
                message.get(
                    "answer",
                    "No answer available."
                )
            )

            # ================================================
            # SQL QUERY
            # ================================================

            sql = message.get("sql")

            if sql:

                st.markdown("### 🧠 SQL Query")

                st.code(
                    sql,
                    language="sql"
                )

            # ================================================
            # DATABASE RESULT
            # ================================================

            data = message.get("data")

            if data:

                st.markdown("### 📊 Database Result")

                try:

                    if isinstance(data, list):

                        if len(data) > 0:

                            df = pd.DataFrame(data)

                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True
                            )

                        else:

                            st.info(
                                "No matching records found."
                            )

                    elif isinstance(data, dict):

                        df = pd.DataFrame([data])

                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.write(data)

                except Exception:

                    st.write(data)

            # ================================================
            # DETAILS
            # ================================================

            result_type = message.get(
                "type"
            )

            intent = message.get(
                "intent"
            )

            if result_type or intent:

                with st.expander(
                    "🔎 Query Details"
                ):

                    if result_type:

                        st.write(
                            "**Type:**",
                            result_type
                        )

                    if intent:

                        st.write(
                            "**Intent:**",
                            intent
                        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Message AI Business Assistant..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    question = question.strip()

    if question:

        # ----------------------------------------------------
        # SAVE USER QUESTION
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        # ----------------------------------------------------
        # PROCESS QUESTION
        # ----------------------------------------------------

        with st.spinner(
            "Analyzing your question..."
        ):

            try:

                result = route_question(
                    question
                )

                # --------------------------------------------
                # SAVE COMPLETE RESULT
                # --------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",

                        "answer": result.get(
                            "answer",
                            "No answer available."
                        ),

                        "sql": result.get(
                            "sql"
                        ),

                        "data": result.get(
                            "data"
                        ),

                        "type": result.get(
                            "type"
                        ),

                        "intent": result.get(
                            "intent",
                            ""
                        )
                    }
                )

            except Exception as e:

                print(
                    f"[FRONTEND ERROR] {e}"
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",

                        "answer": (
                            "Sorry, I couldn't process "
                            "your question right now."
                        ),

                        "sql": None,

                        "data": None,

                        "type": "error",

                        "intent": str(e)
                    }
                )

        st.rerun()

    except requests.exceptions.ConnectionError:
        return None


# =========================================================
# AI QUESTION
# =========================================================

def ask_ai(question):
    try:
        response = requests.post(
            f"{API_URL}/ask-ai",
            json={"question": question}
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.exceptions.ConnectionError:
        return None


# =========================================================
# TITLE
# =========================================================

st.title("🤖 AI Business Assistant")


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "📊 Dashboard",
        "👥 Customers",
        "📦 Products",
        "🏷️ Categories",
        "🏭 Suppliers",
        "🛒 Orders",
        "📋 Order Items",
        "💳 Payments",
        "👨‍💼 Employees",
        "📦 Purchase Orders",
        "📋 Purchase Items",
        "📊 Inventory",
        "🔐 Roles",
        "👤 Users",
        "📝 Audit Logs",
        "🤖 AI Assistant"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "📊 Dashboard":

    st.header("📊 Business Dashboard")

    customers = get_data("/customers")
    products = get_data("/products")
    orders = get_data("/orders")
    payments = get_data("/payments")
    employees = get_data("/employees")
    suppliers = get_data("/suppliers")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "👥 Customers",
            len(customers) if customers else 0
        )

    with col2:
        st.metric(
            "📦 Products",
            len(products) if products else 0
        )

    with col3:
        st.metric(
            "🏭 Suppliers",
            len(suppliers) if suppliers else 0
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "🛒 Orders",
            len(orders) if orders else 0
        )

    with col5:
        st.metric(
            "💳 Payments",
            len(payments) if payments else 0
        )

    with col6:
        st.metric(
            "👨‍💼 Employees",
            len(employees) if employees else 0
        )


# =========================================================
# CUSTOMERS
# =========================================================

elif page == "👥 Customers":

    st.header("👥 Customer List")

    customers = get_data("/customers")

    if customers is not None:
        df = pd.DataFrame(customers)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# PRODUCTS
# =========================================================

elif page == "📦 Products":

    st.header("📦 Product List")

    products = get_data("/products")

    if products is not None:
        df = pd.DataFrame(products)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# CATEGORIES
# =========================================================

elif page == "🏷️ Categories":

    st.header("🏷️ Category List")

    categories = get_data("/categories")

    if categories is not None:
        df = pd.DataFrame(categories)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# SUPPLIERS
# =========================================================

elif page == "🏭 Suppliers":

    st.header("🏭 Supplier List")

    suppliers = get_data("/suppliers")

    if suppliers is not None:
        df = pd.DataFrame(suppliers)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# ORDERS
# =========================================================

elif page == "🛒 Orders":

    st.header("🛒 Order List")

    orders = get_data("/orders")

    if orders is not None:
        df = pd.DataFrame(orders)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# ORDER ITEMS
# =========================================================

elif page == "📋 Order Items":

    st.header("📋 Order Items")

    items = get_data("/order-items")

    if items is not None:
        df = pd.DataFrame(items)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# PAYMENTS
# =========================================================

elif page == "💳 Payments":

    st.header("💳 Payment List")

    payments = get_data("/payments")

    if payments is not None:
        df = pd.DataFrame(payments)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# EMPLOYEES
# =========================================================

elif page == "👨‍💼 Employees":

    st.header("👨‍💼 Employee List")

    employees = get_data("/employees")

    if employees is not None:
        df = pd.DataFrame(employees)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# PURCHASE ORDERS
# =========================================================

elif page == "📦 Purchase Orders":

    st.header("📦 Purchase Orders")

    purchase_orders = get_data("/purchase-orders")

    if purchase_orders is not None:
        df = pd.DataFrame(purchase_orders)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# PURCHASE ITEMS
# =========================================================

elif page == "📋 Purchase Items":

    st.header("📋 Purchase Items")

    purchase_items = get_data("/purchase-items")

    if purchase_items is not None:
        df = pd.DataFrame(purchase_items)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# INVENTORY
# =========================================================

elif page == "📊 Inventory":

    st.header("📊 Inventory Transactions")

    inventory = get_data("/inventory-transactions")

    if inventory is not None:
        df = pd.DataFrame(inventory)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# ROLES
# =========================================================

elif page == "🔐 Roles":

    st.header("🔐 Roles")

    roles = get_data("/roles")

    if roles is not None:
        df = pd.DataFrame(roles)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# USERS
# =========================================================

elif page == "👤 Users":

    st.header("👤 Users")

    users = get_data("/users")

    if users is not None:
        df = pd.DataFrame(users)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# AUDIT LOGS
# =========================================================

elif page == "📝 Audit Logs":

    st.header("📝 Audit Logs")

    logs = get_data("/audit-logs")

    if logs is not None:
        df = pd.DataFrame(logs)
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Could not connect to FastAPI")


# =========================================================
# AI ASSISTANT
# =========================================================

elif page == "🤖 AI Assistant":

    st.header("💬 Ask Your Business Question")

    st.info(
        "Ask questions about your business data."
    )

    question = st.text_input(
        "Ask your business question",
        placeholder="Example: How many customers do we have?"
    )

    if st.button("Ask AI"):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            result = ask_ai(question)

            if result is not None:

                st.write("### Your Question")

                st.write(question)

                st.success(result["answer"])

            else:

                st.error(
                    "Could not connect to FastAPI. "
                    "Make sure the backend is running."
                )
