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

        return None

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