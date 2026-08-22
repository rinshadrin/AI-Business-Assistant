import os
import sys

# =========================================================
# PROJECT ROOT
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, BASE_DIR)


# =========================================================
# DATABASE
# =========================================================

from backend.db import SessionLocal, engine

from backend.models import (
    Customer,
    Product,
    Category,
    Supplier,
    Employee,
    Order,
    OrderItem,
    InventoryTransaction,
    PurchaseOrder,
    PurchaseItem,
    Payment
)


# =========================================================
# SQLAlchemy
# =========================================================

from sqlalchemy import inspect


# =========================================================
# CHROMA
# =========================================================

from rag.vector_store import add_documents


# =========================================================
# BUSINESS DATA INGESTION
# =========================================================

def ingest_business_data():

    session = SessionLocal()

    documents = []
    ids = []
    metadatas = []

    try:

        # =================================================
        # LOAD ALL BASE TABLES
        # =================================================

        customers = session.query(Customer).all()
        products = session.query(Product).all()
        categories = session.query(Category).all()
        suppliers = session.query(Supplier).all()
        employees = session.query(Employee).all()
        orders = session.query(Order).all()
        order_items = session.query(OrderItem).all()
        transactions = session.query(InventoryTransaction).all()
        purchase_orders = session.query(PurchaseOrder).all()
        purchase_items = session.query(PurchaseItem).all()
        payments = session.query(Payment).all()

        # =================================================
        # LOOKUP DICTIONARIES
        # =================================================

        customer_lookup = {
            c.customer_id: c.customer_name
            for c in customers
        }

        product_lookup = {
            p.product_id: p.product_name
            for p in products
        }

        category_lookup = {
            c.category_id: c.category_name
            for c in categories
        }

        supplier_lookup = {
            s.supplier_id: s.supplier_name
            for s in suppliers
        }

        employee_lookup = {
            e.employee_id: e.employee_name
            for e in employees
        }

        # =================================================
        # CUSTOMERS
        # =================================================

        for customer in customers:

            document = (
                f"Customer {customer.customer_name}. "
                f"Email: {customer.email}. "
                f"Phone: {customer.phone}. "
                f"City: {customer.city}."
            )

            documents.append(document)

            ids.append(
                f"customer_{customer.customer_id}"
            )

            metadatas.append({
                "type": "customer",
                "id": str(customer.customer_id)
            })

        # =================================================
        # PRODUCTS
        # =================================================

        for product in products:

            category_name = category_lookup.get(
                product.category_id,
                "Unknown category"
            )

            supplier_name = supplier_lookup.get(
                product.supplier_id,
                "Unknown supplier"
            )

            document = (
                f"Product {product.product_name}. "
                f"Unit price: {product.unit_price}. "
                f"Current stock: {product.stock_quantity}. "
                f"Reorder level: {product.reorder_level}. "
                f"Category: {category_name}. "
                f"Supplier: {supplier_name}."
            )

            documents.append(document)

            ids.append(
                f"product_{product.product_id}"
            )

            metadatas.append({
                "type": "product",
                "id": str(product.product_id),
                "category_id": str(product.category_id),
                "supplier_id": str(product.supplier_id)
            })

        # =================================================
        # CATEGORIES
        # =================================================

        for category in categories:

            document = (
                f"Category {category.category_name}. "
                f"Description: {category.description}."
            )

            documents.append(document)

            ids.append(
                f"category_{category.category_id}"
            )

            metadatas.append({
                "type": "category",
                "id": str(category.category_id)
            })

        # =================================================
        # SUPPLIERS
        # =================================================

        for supplier in suppliers:

            document = (
                f"Supplier {supplier.supplier_name}. "
                f"Contact person: {supplier.contact_person}. "
                f"Email: {supplier.email}. "
                f"Phone: {supplier.phone}. "
                f"City: {supplier.city}."
            )

            documents.append(document)

            ids.append(
                f"supplier_{supplier.supplier_id}"
            )

            metadatas.append({
                "type": "supplier",
                "id": str(supplier.supplier_id)
            })

        # =================================================
        # EMPLOYEES
        # =================================================

        for employee in employees:

            document = (
                f"Employee {employee.employee_name}. "
                f"Department: {employee.department}. "
                f"Job title: {employee.job_title}. "
                f"Employment status: "
                f"{employee.employment_status}."
            )

            documents.append(document)

            ids.append(
                f"employee_{employee.employee_id}"
            )

            metadatas.append({
                "type": "employee",
                "id": str(employee.employee_id)
            })

        # =================================================
        # ORDERS
        # =================================================

        for order in orders:

            customer_name = customer_lookup.get(
                order.customer_id,
                "Unknown customer"
            )

            document = (
                f"Customer order {order.order_id}. "
                f"Customer: {customer_name}. "
                f"Order date: {order.order_date}. "
                f"Status: {order.order_status}. "
                f"Total amount: {order.total_amount}."
            )

            documents.append(document)

            ids.append(
                f"order_{order.order_id}"
            )

            metadatas.append({
                "type": "order",
                "id": str(order.order_id),
                "customer_id": str(order.customer_id)
            })

        # =================================================
        # ORDER ITEMS
        # =================================================

        for item in order_items:

            product_name = product_lookup.get(
                item.product_id,
                "Unknown product"
            )

            document = (
                f"Order item {item.order_item_id}. "
                f"Order ID: {item.order_id}. "
                f"Product: {product_name}. "
                f"Quantity: {item.quantity}. "
                f"Unit price: {item.unit_price}."
            )

            documents.append(document)

            ids.append(
                f"order_item_{item.order_item_id}"
            )

            metadatas.append({
                "type": "order_item",
                "id": str(item.order_item_id),
                "order_id": str(item.order_id),
                "product_id": str(item.product_id)
            })

        # =================================================
        # INVENTORY TRANSACTIONS
        # =================================================

        for transaction in transactions:

            product_name = product_lookup.get(
                transaction.product_id,
                "Unknown product"
            )

            document = (
                f"Inventory transaction "
                f"{transaction.transaction_id}. "
                f"Product: {product_name}. "
                f"Transaction type: "
                f"{transaction.transaction_type}. "
                f"Quantity: {transaction.quantity}. "
                f"Transaction date: "
                f"{transaction.transaction_date}. "
                f"Reference type: "
                f"{transaction.reference_type}. "
                f"Reference ID: "
                f"{transaction.reference_id}. "
                f"Remarks: {transaction.remarks}."
            )

            documents.append(document)

            ids.append(
                f"inventory_transaction_"
                f"{transaction.transaction_id}"
            )

            metadatas.append({
                "type": "inventory_transaction",
                "id": str(transaction.transaction_id),
                "product_id": str(transaction.product_id)
            })

        # =================================================
        # PURCHASE ORDERS
        # =================================================

        for purchase_order in purchase_orders:

            supplier_name = supplier_lookup.get(
                purchase_order.supplier_id,
                "Unknown supplier"
            )

            employee_name = employee_lookup.get(
                purchase_order.employee_id,
                "Unknown employee"
            )

            document = (
                f"Purchase order "
                f"{purchase_order.purchase_order_id}. "
                f"Supplier: {supplier_name}. "
                f"Employee: {employee_name}. "
                f"Purchase date: "
                f"{purchase_order.purchase_date}. "
                f"Status: "
                f"{purchase_order.order_status}. "
                f"Total amount: "
                f"{purchase_order.total_amount}."
            )

            documents.append(document)

            ids.append(
                f"purchase_order_"
                f"{purchase_order.purchase_order_id}"
            )

            metadatas.append({
                "type": "purchase_order",
                "id": str(purchase_order.purchase_order_id),
                "supplier_id": str(purchase_order.supplier_id),
                "employee_id": str(purchase_order.employee_id)
            })

        # =================================================
        # PURCHASE ITEMS
        # =================================================

        for item in purchase_items:

            product_name = product_lookup.get(
                item.product_id,
                "Unknown product"
            )

            document = (
                f"Purchase item "
                f"{item.purchase_item_id}. "
                f"Purchase order ID: "
                f"{item.purchase_order_id}. "
                f"Product: {product_name}. "
                f"Quantity: {item.quantity}. "
                f"Unit price: {item.unit_price}."
            )

            documents.append(document)

            ids.append(
                f"purchase_item_{item.purchase_item_id}"
            )

            metadatas.append({
                "type": "purchase_item",
                "id": str(item.purchase_item_id),
                "purchase_order_id": str(item.purchase_order_id),
                "product_id": str(item.product_id)
            })

        # =================================================
        # PAYMENTS
        # =================================================

        for payment in payments:

            document = (
                f"Payment {payment.payment_id}. "
                f"Order ID: {payment.order_id}. "
                f"Payment method: "
                f"{payment.payment_method}. "
                f"Payment date: "
                f"{payment.payment_date}. "
                f"Amount: {payment.amount}. "
                f"Payment status: "
                f"{payment.payment_status}."
            )

            documents.append(document)

            ids.append(
                f"payment_{payment.payment_id}"
            )

            metadatas.append({
                "type": "payment",
                "id": str(payment.payment_id),
                "order_id": str(payment.order_id)
            })

        # =================================================
        # SAVE BUSINESS DATA
        # =================================================

        if documents:

            add_documents(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )

            print(
                f"✅ Business records indexed: "
                f"{len(documents)}"
            )

    finally:

        session.close()


# =========================================================
# DATABASE SCHEMA INGESTION
# =========================================================

def index_database_schema():

    print("\n🔍 Reading database schema...")

    inspector = inspect(engine)

    documents = []
    ids = []
    metadatas = []

    tables = inspector.get_table_names()

    print(
        f"📋 Found {len(tables)} database tables."
    )

    for table_name in tables:

        # =================================================
        # COLUMNS
        # =================================================

        columns = inspector.get_columns(
            table_name
        )

        # =================================================
        # PRIMARY KEY
        # =================================================

        primary_key_info = (
            inspector.get_pk_constraint(
                table_name
            )
        )

        primary_keys = primary_key_info.get(
            "constrained_columns",
            []
        )

        # =================================================
        # FOREIGN KEYS
        # =================================================

        foreign_keys = inspector.get_foreign_keys(
            table_name
        )

        lines = []

        lines.append(
            f"TABLE: {table_name}"
        )

        lines.append(
            "COLUMNS:"
        )

        for column in columns:

            column_name = column["name"]

            column_type = str(
                column["type"]
            )

            nullable = column.get(
                "nullable",
                True
            )

            flags = []

            if column_name in primary_keys:
                flags.append(
                    "PRIMARY KEY"
                )

            if not nullable:
                flags.append(
                    "NOT NULL"
                )

            flag_text = ""

            if flags:
                flag_text = (
                    " [" +
                    ", ".join(flags) +
                    "]"
                )

            lines.append(
                f"- {column_name} | "
                f"TYPE: {column_type}"
                f"{flag_text}"
            )

        # =================================================
        # FOREIGN KEY RELATIONSHIPS
        # =================================================

        lines.append(
            ""
        )

        lines.append(
            "FOREIGN KEY RELATIONSHIPS:"
        )

        if foreign_keys:

            for foreign_key in foreign_keys:

                constrained_columns = (
                    foreign_key.get(
                        "constrained_columns",
                        []
                    )
                )

                referred_table = (
                    foreign_key.get(
                        "referred_table"
                    )
                )

                referred_columns = (
                    foreign_key.get(
                        "referred_columns",
                        []
                    )
                )

                for (
                    local_column,
                    remote_column
                ) in zip(
                    constrained_columns,
                    referred_columns
                ):

                    lines.append(
                        f"- {table_name}."
                        f"{local_column}"
                        f" → "
                        f"{referred_table}."
                        f"{remote_column}"
                    )

        else:

            lines.append(
                "- None"
            )

        # =================================================
        # DOCUMENT
        # =================================================

        document = "\n".join(
            lines
        )

        documents.append(
            document
        )

        ids.append(
            f"schema_{table_name}"
        )

        metadatas.append({
            "type": "schema",
            "table": table_name
        })

    # =====================================================
    # SAVE SCHEMA TO CHROMA
    # =====================================================

    if documents:

        add_documents(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

        print(
            f"✅ Database schema indexed: "
            f"{len(documents)} tables"
        )

    else:

        print(
            "⚠️ No database tables found."
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ERP RAG INGESTION")
    print("=" * 60)

    # Existing business data
    ingest_business_data()

    # New schema data for Text-to-SQL
    index_database_schema()

    print("\n" + "=" * 60)
    print("✅ RAG INGESTION COMPLETED")
    print("=" * 60)