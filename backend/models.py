from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
    DECIMAL,
    Text
)
from sqlalchemy.orm import relationship
from backend.db import Base

# ==========================
# CUSTOMER
# ==========================


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    city = Column(String(100))
    created_at = Column(DateTime)

    orders = relationship("Order", back_populates="customer")

# ==========================
# SUPPLIER
# ==========================

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(150), unique=True)
    phone = Column(String(20))
    city = Column(String(100))
    created_at = Column(DateTime)

    products = relationship("Product", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


# ==========================
# CATEGORY
# ==========================

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime)

    products = relationship("Product", back_populates="category")


# ==========================
# PRODUCT
# ==========================

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)

    product_name = Column(String(150), nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.category_id")
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.supplier_id")
    )

    unit_price = Column(DECIMAL(10, 2))

    stock_quantity = Column(Integer)

    reorder_level = Column(Integer)

    created_at = Column(DateTime)

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")

    order_items = relationship("OrderItem", back_populates="product")
    inventory_transactions = relationship(
        "InventoryTransaction",
        back_populates="product"
    )

    purchase_items = relationship(
        "PurchaseItem",
        back_populates="product"
    )

# ==========================
# EMPLOYEE
# ==========================

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True)
    phone = Column(String(20))
    department = Column(String(50))
    job_title = Column(String(100))
    salary = Column(DECIMAL(10, 2))
    hire_date = Column(Date)
    employment_status = Column(
        Enum("ACTIVE", "INACTIVE", "ON_LEAVE")
    )
    created_at = Column(DateTime)

    users = relationship("User", back_populates="employee")
    purchase_orders = relationship(
        "PurchaseOrder",
        back_populates="employee"
    )


# ==========================
# ROLE
# ==========================

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True)
    description = Column(String(255))

    users = relationship("User", back_populates="role")


# ==========================
# USER
# ==========================

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.employee_id")
    )

    role_id = Column(
        Integer,
        ForeignKey("roles.role_id")
    )

    username = Column(String(50), unique=True)
    password_hash = Column(String(255))
    is_active = Column(Boolean)
    created_at = Column(DateTime)

    employee = relationship("Employee", back_populates="users")
    role = relationship("Role", back_populates="users")

    audit_logs = relationship("AuditLog", back_populates="user")


# ==========================
# ORDER
# ==========================

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id")
    )

    order_date = Column(Date)

    order_status = Column(
        Enum("Pending", "Completed", "Cancelled")
    )

    total_amount = Column(DECIMAL(10, 2))

    customer = relationship("Customer", back_populates="orders")

    order_items = relationship(
        "OrderItem",
        back_populates="order"
    )

    payments = relationship(
        "Payment",
        back_populates="order"
    )


# ==========================
# ORDER ITEM
# ==========================

class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id")
    )

    quantity = Column(Integer)

    unit_price = Column(DECIMAL(10, 2))

    order = relationship("Order", back_populates="order_items")

    product = relationship(
        "Product",
        back_populates="order_items"
    )

# ==========================
# INVENTORY TRANSACTION
# ==========================

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.product_id")
    )

    transaction_type = Column(
        Enum(
            "PURCHASE",
            "SALE",
            "CUSTOMER_RETURN",
            "SUPPLIER_RETURN",
            "ADJUSTMENT_IN",
            "ADJUSTMENT_OUT"
        )
    )

    quantity = Column(Integer)

    transaction_date = Column(DateTime)

    reference_type = Column(
        Enum(
            "PURCHASE_ORDER",
            "CUSTOMER_ORDER",
            "MANUAL"
        )
    )

    reference_id = Column(Integer)

    remarks = Column(String(255))

    product = relationship(
        "Product",
        back_populates="inventory_transactions"
    )


# ==========================
# PURCHASE ORDER
# ==========================

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    purchase_order_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.supplier_id")
    )

    employee_id = Column(
        Integer,
        ForeignKey("employees.employee_id")
    )

    purchase_date = Column(Date)

    order_status = Column(
        Enum(
            "Pending",
            "Received",
            "Cancelled"
        )
    )

    total_amount = Column(DECIMAL(10, 2))

    supplier = relationship(
        "Supplier",
        back_populates="purchase_orders"
    )

    employee = relationship(
        "Employee",
        back_populates="purchase_orders"
    )

    purchase_items = relationship(
        "PurchaseItem",
        back_populates="purchase_order"
    )


# ==========================
# PURCHASE ITEM
# ==========================

class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    purchase_item_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.purchase_order_id")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id")
    )

    quantity = Column(Integer)

    unit_price = Column(DECIMAL(10, 2))

    purchase_order = relationship(
        "PurchaseOrder",
        back_populates="purchase_items"
    )

    product = relationship(
        "Product",
        back_populates="purchase_items"
    )


# ==========================
# PAYMENT
# ==========================

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id")
    )

    payment_method = Column(
        Enum(
            "Cash",
            "UPI",
            "Credit Card",
            "Debit Card",
            "Net Banking"
        )
    )

    payment_date = Column(Date)

    amount = Column(DECIMAL(10, 2))

    payment_status = Column(
        Enum(
            "Pending",
            "Completed",
            "Failed",
            "Refunded"
        )
    )

    order = relationship(
        "Order",
        back_populates="payments"
    )


# ==========================
# AUDIT LOG
# ==========================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id")
    )

    action_type = Column(String(50))

    table_name = Column(String(100))

    record_id = Column(Integer)

    action_time = Column(DateTime)

    description = Column(String(255))

    user = relationship(
        "User",
        back_populates="audit_logs"
    )