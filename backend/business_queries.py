from backend.db import SessionLocal

from backend.models import (
    Customer,
    Product,
    Category,
    Supplier,
    Order,
    Payment,
    PurchaseOrder,
)


# =====================================================
# GET ALL CATEGORIES
# =====================================================

def get_all_categories():
    session = SessionLocal()

    try:
        categories = (
            session.query(Category)
            .order_by(Category.category_id)
            .all()
        )

        return [
            {
                "id": category.category_id,
                "name": category.category_name,
                "description": category.description
            }
            for category in categories
        ]

    finally:
        session.close()


# =====================================================
# GET PRODUCT CATEGORIES
# =====================================================

def get_product_categories():
    session = SessionLocal()

    try:
        categories = (
            session.query(Category)
            .order_by(Category.category_id)
            .all()
        )

        return [
            {
                "id": category.category_id,
                "name": category.category_name,
                "description": category.description
            }
            for category in categories
        ]

    finally:
        session.close()


# =====================================================
# GET ALL PRODUCTS
# =====================================================

def get_all_products():
    session = SessionLocal()

    try:
        products = (
            session.query(Product)
            .order_by(Product.product_id)
            .all()
        )

        return [
            {
                "id": product.product_id,
                "name": product.product_name,
                "stock": product.stock_quantity,
                "reorder_level": product.reorder_level,
                "result_type": "all_products"
            }
            for product in products
        ]

    finally:
        session.close()


# =====================================================
# CUSTOMER COUNT
# =====================================================

def get_customer_count():
    session = SessionLocal()

    try:
        return session.query(Customer).count()

    finally:
        session.close()


# =====================================================
# PRODUCT COUNT
# =====================================================

def get_product_count():
    session = SessionLocal()

    try:
        return session.query(Product).count()

    finally:
        session.close()


# =====================================================
# CATEGORY DESCRIPTION
# =====================================================

def get_category_description(category_name):
    session = SessionLocal()

    try:
        category = (
            session.query(Category)
            .filter(
                Category.category_name.ilike(category_name)
            )
            .first()
        )

        if not category:
            return None

        return {
            "name": category.category_name,
            "description": category.description
        }

    finally:
        session.close()


# =====================================================
# LOW STOCK PRODUCTS
# =====================================================

def get_low_stock_products():
    session = SessionLocal()

    try:
        products = (
            session.query(Product)
            .filter(
                Product.stock_quantity <= Product.reorder_level
            )
            .all()
        )

        return [
            {
                "name": product.product_name,
                "stock": product.stock_quantity,
                "reorder_level": product.reorder_level,
                "result_type": "low_stock"
            }
            for product in products
        ]

    finally:
        session.close()


# =====================================================
# TOTAL PAYMENTS
# =====================================================

def get_total_payment():
    session = SessionLocal()

    try:
        payments = session.query(Payment).all()

        total = sum(
            float(payment.amount)
            for payment in payments
            if payment.amount is not None
        )

        return total

    finally:
        session.close()


# =====================================================
# PENDING ORDERS
# =====================================================

def get_pending_orders():
    session = SessionLocal()

    try:
        orders = (
            session.query(Order)
            .filter(
                Order.order_status == "Pending"
            )
            .all()
        )

        return [
            {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "date": str(order.order_date),
                "total_amount": (
                    float(order.total_amount)
                    if order.total_amount is not None
                    else 0
                )
            }
            for order in orders
        ]

    finally:
        session.close()


# =====================================================
# SUPPLIER COUNT
# =====================================================

def get_supplier_count():
    session = SessionLocal()

    try:
        return session.query(Supplier).count()

    finally:
        session.close()


# =====================================================
# PURCHASE ORDER COUNT
# =====================================================

def get_purchase_order_count():
    session = SessionLocal()

    try:
        return session.query(PurchaseOrder).count()

    finally:
        session.close()


# =====================================================
# FINANCIAL SUMMARY
# =====================================================

def get_financial_summary():
    """
    Calculate the current financial position.

    Revenue:
        Only COMPLETED customer orders.

    Expenses:
        Only RECEIVED purchase orders.

    Profit:
        Revenue - Expenses

    Profit Margin:
        Profit / Revenue * 100
    """

    session = SessionLocal()

    try:

        # =================================================
        # COMPLETED SALES
        # =================================================

        completed_sales = (
            session.query(Order)
            .filter(
                Order.order_status == "Completed"
            )
            .all()
        )

        total_sales = sum(
            float(order.total_amount or 0)
            for order in completed_sales
        )

        # =================================================
        # RECEIVED PURCHASES
        # =================================================

        received_purchases = (
            session.query(PurchaseOrder)
            .filter(
                PurchaseOrder.order_status == "Received"
            )
            .all()
        )

        total_purchases = sum(
            float(purchase.total_amount or 0)
            for purchase in received_purchases
        )

        # =================================================
        # PROFIT / LOSS
        # =================================================

        profit_loss = (
            total_sales - total_purchases
        )

        # =================================================
        # PROFIT MARGIN
        # =================================================

        if total_sales > 0:

            profit_margin = (
                profit_loss / total_sales
            ) * 100

        else:

            profit_margin = 0.0

        # =================================================
        # RESULT
        # =================================================

        return {
            "total_sales": round(
                total_sales,
                2
            ),

            "total_purchases": round(
                total_purchases,
                2
            ),

            "profit_loss": round(
                profit_loss,
                2
            ),

            "profit_margin": round(
                profit_margin,
                2
            ),

            "status": (
                "PROFIT"
                if profit_loss > 0
                else
                "LOSS"
                if profit_loss < 0
                else
                "BREAK-EVEN"
            ),

            "result_type": "financial_summary"
        }

    finally:
        session.close()


# =====================================================
# TOTAL SALES
# =====================================================

def get_total_sales():
    session = SessionLocal()

    try:
        orders = (
            session.query(Order)
            .filter(
                Order.order_status == "Completed"
            )
            .all()
        )

        return sum(
            float(order.total_amount or 0)
            for order in orders
        )

    finally:
        session.close()


# =====================================================
# TOTAL PURCHASE COST
# =====================================================

def get_total_purchases():
    session = SessionLocal()

    try:
        purchases = (
            session.query(PurchaseOrder)
            .filter(
                PurchaseOrder.order_status.in_(
                    ["Received"]
                )
            )
            .all()
        )

        return sum(
            float(purchase.total_amount or 0)
            for purchase in purchases
        )

    finally:
        session.close()


# =====================================================
# PROFIT / LOSS
# =====================================================

def get_profit():
    sales = get_total_sales()
    purchases = get_total_purchases()

    profit = sales - purchases

    return {
        "sales": round(sales, 2),
        "purchases": round(purchases, 2),
        "profit": round(profit, 2),
        "result": (
            "profit"
            if profit > 0
            else "loss"
            if profit < 0
            else "break-even"
        )
    }


# =====================================================
# PROFIT PERCENTAGE
# =====================================================

def get_profit_percentage():
    sales = get_total_sales()
    purchases = get_total_purchases()

    if sales == 0:
        return {
            "sales": 0,
            "purchases": round(purchases, 2),
            "profit": round(sales - purchases, 2),
            "profit_percentage": 0
        }

    profit = sales - purchases

    percentage = (
        profit / sales
    ) * 100

    return {
        "sales": round(sales, 2),
        "purchases": round(purchases, 2),
        "profit": round(profit, 2),
        "profit_percentage": round(
            percentage,
            2
        )
    }