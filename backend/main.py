from fastapi import FastAPI
from pydantic import BaseModel

from backend.db import SessionLocal

from backend.models import (
    Customer,
    Product,
    Category,
    Supplier,
    Order,
    OrderItem,
    Payment,
    Employee,
    PurchaseOrder,
    PurchaseItem,
    InventoryTransaction,
    Role,
    User,
    AuditLog
)

from backend.ai_service import answer_business_question


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI()


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "AI Business Assistant API Running"
    }


# =========================================================
# CUSTOMERS
# =========================================================

@app.get("/customers")
def get_customers():

    session = SessionLocal()

    try:

        customers = session.query(Customer).all()

        data = []

        for customer in customers:

            data.append({
                "id": customer.customer_id,
                "name": customer.customer_name,
                "email": customer.email,
                "phone": customer.phone,
                "city": customer.city
            })

        return data

    finally:
        session.close()


# =========================================================
# PRODUCTS
# =========================================================

@app.get("/products")
def get_products():

    session = SessionLocal()

    try:

        products = session.query(Product).all()

        data = []

        for product in products:

            data.append({
                "id": product.product_id,
                "name": product.product_name,
                "category_id": product.category_id,
                "supplier_id": product.supplier_id,
                "unit_price": float(product.unit_price),
                "stock_quantity": product.stock_quantity,
                "reorder_level": product.reorder_level
            })

        return data

    finally:
        session.close()


# =========================================================
# CATEGORIES
# =========================================================

@app.get("/categories")
def get_categories():

    session = SessionLocal()

    try:

        categories = session.query(Category).all()

        data = []

        for category in categories:

            data.append({
                "id": category.category_id,
                "name": category.category_name,
                "description": category.description
            })

        return data

    finally:
        session.close()


# =========================================================
# SUPPLIERS
# =========================================================

@app.get("/suppliers")
def get_suppliers():

    session = SessionLocal()

    try:

        suppliers = session.query(Supplier).all()

        data = []

        for supplier in suppliers:

            data.append({
                "id": supplier.supplier_id,
                "name": supplier.supplier_name,
                "contact_person": supplier.contact_person,
                "email": supplier.email,
                "phone": supplier.phone,
                "city": supplier.city
            })

        return data

    finally:
        session.close()


# =========================================================
# ORDERS
# =========================================================

@app.get("/orders")
def get_orders():

    session = SessionLocal()

    try:

        orders = session.query(Order).all()

        data = []

        for order in orders:

            data.append({
                "id": order.order_id,
                "customer_id": order.customer_id,
                "order_date": order.order_date,
                "order_status": order.order_status,
                "total_amount": float(order.total_amount)
            })

        return data

    finally:
        session.close()


# =========================================================
# ORDER ITEMS
# =========================================================

@app.get("/order-items")
def get_order_items():

    session = SessionLocal()

    try:

        items = session.query(OrderItem).all()

        data = []

        for item in items:

            data.append({
                "id": item.order_item_id,
                "order_id": item.order_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price)
            })

        return data

    finally:
        session.close()


# =========================================================
# PAYMENTS
# =========================================================

@app.get("/payments")
def get_payments():

    session = SessionLocal()

    try:

        payments = session.query(Payment).all()

        data = []

        for payment in payments:

            data.append({
                "id": payment.payment_id,
                "order_id": payment.order_id,
                "payment_method": payment.payment_method,
                "payment_date": payment.payment_date,
                "amount": float(payment.amount),
                "payment_status": payment.payment_status
            })

        return data

    finally:
        session.close()


# =========================================================
# EMPLOYEES
# =========================================================

@app.get("/employees")
def get_employees():

    session = SessionLocal()

    try:

        employees = session.query(Employee).all()

        data = []

        for employee in employees:

            data.append({
                "id": employee.employee_id,
                "name": employee.employee_name,
                "email": employee.email,
                "phone": employee.phone,
                "department": employee.department,
                "job_title": employee.job_title,
                "salary": float(employee.salary),
                "hire_date": employee.hire_date,
                "employment_status": employee.employment_status
            })

        return data

    finally:
        session.close()


# =========================================================
# PURCHASE ORDERS
# =========================================================

@app.get("/purchase-orders")
def get_purchase_orders():

    session = SessionLocal()

    try:

        purchase_orders = session.query(PurchaseOrder).all()

        data = []

        for purchase_order in purchase_orders:

            data.append({
                "id": purchase_order.purchase_order_id,
                "supplier_id": purchase_order.supplier_id,
                "employee_id": purchase_order.employee_id,
                "purchase_date": purchase_order.purchase_date,
                "order_status": purchase_order.order_status,
                "total_amount": float(
                    purchase_order.total_amount
                )
            })

        return data

    finally:
        session.close()


# =========================================================
# PURCHASE ITEMS
# =========================================================

@app.get("/purchase-items")
def get_purchase_items():

    session = SessionLocal()

    try:

        items = session.query(PurchaseItem).all()

        data = []

        for item in items:

            data.append({
                "id": item.purchase_item_id,
                "purchase_order_id": item.purchase_order_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price)
            })

        return data

    finally:
        session.close()


# =========================================================
# INVENTORY TRANSACTIONS
# =========================================================

@app.get("/inventory-transactions")
def get_inventory_transactions():

    session = SessionLocal()

    try:

        transactions = session.query(
            InventoryTransaction
        ).all()

        data = []

        for transaction in transactions:

            data.append({
                "id": transaction.transaction_id,
                "product_id": transaction.product_id,
                "transaction_type": transaction.transaction_type,
                "quantity": transaction.quantity,
                "transaction_date": transaction.transaction_date,
                "reference_type": transaction.reference_type,
                "reference_id": transaction.reference_id,
                "remarks": transaction.remarks
            })

        return data

    finally:
        session.close()


# =========================================================
# ROLES
# =========================================================

@app.get("/roles")
def get_roles():

    session = SessionLocal()

    try:

        roles = session.query(Role).all()

        data = []

        for role in roles:

            data.append({
                "id": role.role_id,
                "role_name": role.role_name,
                "description": role.description
            })

        return data

    finally:
        session.close()


# =========================================================
# USERS
# =========================================================

@app.get("/users")
def get_users():

    session = SessionLocal()

    try:

        users = session.query(User).all()

        data = []

        for user in users:

            data.append({
                "id": user.user_id,
                "employee_id": user.employee_id,
                "role_id": user.role_id,
                "username": user.username,
                "is_active": user.is_active,
                "created_at": user.created_at
            })

        return data

    finally:
        session.close()


# =========================================================
# AUDIT LOGS
# =========================================================

@app.get("/audit-logs")
def get_audit_logs():

    session = SessionLocal()

    try:

        logs = session.query(AuditLog).all()

        data = []

        for log in logs:

            data.append({
                "id": log.log_id,
                "user_id": log.user_id,
                "action_type": log.action_type,
                "table_name": log.table_name,
                "record_id": log.record_id,
                "action_time": log.action_time,
                "description": log.description
            })

        return data

    finally:
        session.close()


# =========================================================
# AI ASSISTANT - LLM + RAG
# =========================================================

class AIQuestion(BaseModel):
    question: str


@app.post("/ask-ai")
def ask_ai(data: AIQuestion):

    question = data.question.strip()

    # -----------------------------------------------------
    # EMPTY QUESTION
    # -----------------------------------------------------

    if not question:

        return {
            "question": data.question,
            "answer": "Please enter a business question."
        }

    # -----------------------------------------------------
    # LLM + RAG PIPELINE
    # -----------------------------------------------------

    try:

        answer = answer_business_question(question)

        return {
            "question": data.question,
            "answer": answer
        }

    except Exception as e:

        return {
            "question": data.question,
            "answer": (
                "Unable to process the business question. "
                f"Error: {str(e)}"
            )
        }