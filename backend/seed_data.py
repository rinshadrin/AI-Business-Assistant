from faker import Faker
from db import SessionLocal
from models import Customer, Product

fake = Faker()
session = SessionLocal()

# -------------------------
# CUSTOMERS
# -------------------------
customer_count = session.query(Customer).count()

for i in range(max(0, 50 - customer_count)):
    customer = Customer(
        customer_name=fake.name(),
        email=fake.unique.email(),
        phone=fake.numerify("##########"),
        city=fake.city()
    )
    session.add(customer)

session.commit()

print("✅ Customers checked/updated!")


# -------------------------
# PRODUCTS
# -------------------------
product_count = session.query(Product).count()

categories = [1, 2, 3, 4, 5]
suppliers = [1, 2, 3, 4, 5]

for i in range(max(0, 50 - product_count)):
    price = round(
    fake.random.uniform(100, 100000),
    2
)

    stock = fake.random_int(min=10, max=200)
    reorder_level = fake.random_int(min=5, max=30)

    product = Product(
        product_name=fake.catch_phrase(),
        category_id=fake.random_element(categories),
        supplier_id=fake.random_element(suppliers),
        unit_price=price,
        stock_quantity=stock,
        reorder_level=reorder_level
    )

    session.add(product)

session.commit()

print("✅ Products checked/updated!")

session.close()

print("🎉 Database seeding completed!")


# -------------------------
# SUPPLIERS
# -------------------------
from models import Supplier

supplier_count = session.query(Supplier).count()

for i in range(max(0, 50 - supplier_count)):

    supplier = Supplier(
        supplier_name=fake.company(),
        contact_person=fake.name(),
        email=fake.unique.email(),
        phone=fake.numerify("##########"),
        city=fake.city()
    )

    session.add(supplier)

session.commit()

print("✅ Suppliers checked/updated!")

# -------------------------
# ORDERS
# -------------------------
from models import Order

order_count = session.query(Order).count()

customer_ids = [
    customer.customer_id
    for customer in session.query(Customer).all()
]

for i in range(max(0, 100 - order_count)):

    order = Order(
        customer_id=fake.random_element(customer_ids),
        order_date=fake.date_time_between(
            start_date="-1y",
            end_date="now"
        ),
        order_status=fake.random_element([
            "Completed",
            "Pending",
            "Cancelled"
        ]),
        total_amount=round(
            fake.random.uniform(500, 100000),
            2
        )
    )

    session.add(order)

session.commit()

print("✅ Orders checked/updated!")

# -------------------------
# PAYMENTS
# -------------------------
from models import Payment

payment_count = session.query(Payment).count()

order_ids = [
    order.order_id
    for order in session.query(Order).all()
]

for i in range(max(0, 100 - payment_count)):

    payment = Payment(
        order_id=fake.random_element(order_ids),
        payment_method=fake.random_element([
            "cash",
            "upi",
            "credit card",
            "debit card"
        ]),
        payment_date=fake.date_time_between(
            start_date="-1y",
            end_date="now"
        ),
        amount=round(
            fake.random.uniform(500, 100000),
            2
        ),
        payment_status=fake.random_element([
            "pending",
            "completed",
            "failed",
            "refunded"
        ])
    )

    session.add(payment)

session.commit()

print("✅ Payments checked/updated!")

# -------------------------
# CATEGORIES
# -------------------------
from models import Category

category_count = session.query(Category).count()

category_names = [
    "Electronics",
    "Clothing",
    "Groceries",
    "Home Appliances",
    "Furniture",
    "Beauty",
    "Sports",
    "Books",
    "Stationery",
    "Footwear",
    "Kitchen",
    "Mobile Accessories",
    "Computer Accessories",
    "Personal Care",
    "Automotive",
    "Toys",
    "Pet Supplies",
    "Office Supplies",
    "Health & Wellness",
    "Garden & Outdoor"
]

for name in category_names[category_count:]:
    category = Category(
        category_name=name,
        description=f"Products related to {name}"
    )

    session.add(category)

session.commit()

print("✅ Categories checked/updated!")

# -------------------------
# ORDER ITEMS
# -------------------------
from models import OrderItem

order_item_count = session.query(OrderItem).count()

orders = session.query(Order).all()
products = session.query(Product).all()

for i in range(max(0, 200 - order_item_count)):

    product = fake.random_element(products)
    order = fake.random_element(orders)

    quantity = fake.random_int(min=1, max=10)

    order_item = OrderItem(
        order_id=order.order_id,
        product_id=product.product_id,
        quantity=quantity,
        unit_price=product.unit_price
    )

    session.add(order_item)

session.commit()

print("✅ Order Items checked/updated!")


# -------------------------
# EMPLOYEES
# -------------------------

from models import Employee

employee_count = session.query(Employee).count()

departments = [
    "HR",
    "Sales",
    "IT",
    "Finance",
    "Marketing",
    "Operations"
]

job_titles = [
    "Manager",
    "Executive",
    "Developer",
    "Accountant",
    "Analyst",
    "Assistant"
]

for i in range(max(0, 30 - employee_count)):

    employee = Employee(
        employee_name=fake.name(),
        email=fake.unique.email(),
        phone=fake.phone_number()[:20],
        department=fake.random_element(departments),
        job_title=fake.random_element(job_titles),
        salary=fake.random_int(min=25000, max=100000),
        hire_date=fake.date_between(start_date="-5y", end_date="today"),
        employment_status=fake.random_element(
            ["ACTIVE", "INACTIVE", "ON_LEAVE"]
        )
    )

    session.add(employee)

session.commit()

print("✅ Employees checked/updated!")

# -------------------------
# PURCHASE ORDERS
# -------------------------
from models import PurchaseOrder, Supplier, Employee

purchase_order_count = session.query(PurchaseOrder).count()

suppliers = session.query(Supplier).all()
employees = session.query(Employee).all()
purchase_order_statuses = [
    "Pending",
    "Received",
    "Cancelled"
]

for i in range(max(0, 50 - purchase_order_count)):

    supplier = fake.random_element(suppliers)
    employee = fake.random_element(employees)

    purchase_order = PurchaseOrder(
        supplier_id=supplier.supplier_id,
        employee_id=employee.employee_id,
        purchase_date=fake.date_between(
            start_date="-1y",
            end_date="today"
        ),
        order_status=fake.random_element(
            purchase_order_statuses
        ),
        total_amount=round(
            fake.random.uniform(5000, 100000),
            2
        )
    )

    session.add(purchase_order)

session.commit()

print("✅ Purchase Orders checked/updated!")

# -------------------------
# PURCHASE ITEMS
# -------------------------
from models import PurchaseItem, PurchaseOrder, Product

purchase_item_count = session.query(PurchaseItem).count()

purchase_orders = session.query(PurchaseOrder).all()
products = session.query(Product).all()

for i in range(max(0, 100 - purchase_item_count)):

    purchase_order = fake.random_element(purchase_orders)
    product = fake.random_element(products)

    purchase_item = PurchaseItem(
        purchase_order_id=purchase_order.purchase_order_id,
        product_id=product.product_id,
        quantity=fake.random_int(min=1, max=50),
        unit_price=round(
            fake.random.uniform(100, 50000),
            2
        )
    )

    session.add(purchase_item)

session.commit()

print("✅ Purchase Items checked/updated!")


# -------------------------
# INVENTORY TRANSACTIONS
# -------------------------
from models import InventoryTransaction, Product

inventory_count = session.query(InventoryTransaction).count()
products = session.query(Product).all()

transaction_types = [
    "PURCHASE",
    "SALE",
    "CUSTOMER_RETURN",
    "SUPPLIER_RETURN",
    "ADJUSTMENT_IN",
    "ADJUSTMENT_OUT"
]

reference_types = [
    "PURCHASE_ORDER",
    "CUSTOMER_ORDER",
    "MANUAL"
]

for i in range(max(0, 50 - inventory_count)):

    product = fake.random_element(products)

    transaction = InventoryTransaction(
        product_id=product.product_id,
        transaction_type=fake.random_element(transaction_types),
        quantity=fake.random_int(min=1, max=50),
        transaction_date=fake.date_time_between(
            start_date="-1y",
            end_date="now"
        ),
        reference_type=fake.random_element(reference_types),
        reference_id=fake.random_int(min=1, max=100),
        remarks=fake.sentence(nb_words=5)
    )

    session.add(transaction)

session.commit()

print("✅ Inventory Transactions checked/updated!")

# -------------------------
# ROLES
# -------------------------
from models import Role

role_count = session.query(Role).count()

roles = [
    ("Admin", "Full system access"),
    ("Manager", "Manages business operations"),
    ("Sales", "Handles customer sales and orders"),
    ("Inventory", "Manages products and inventory"),
    ("Accountant", "Handles payments and financial records")
]

for role_name, description in roles:

    existing_role = session.query(Role).filter(
        Role.role_name == role_name
    ).first()

    if not existing_role and session.query(Role).count() < 5:
        role = Role(
            role_name=role_name,
            description=description
        )
        session.add(role)

session.commit()

print("✅ Roles checked/updated!")

# -------------------------
# USERS
# -------------------------
from models import User, Employee, Role
import hashlib

user_count = session.query(User).count()

employees = session.query(Employee).all()
roles = session.query(Role).all()

for i in range(max(0, 50 - user_count)):

    employee = employees[i % len(employees)]
    role = roles[i % len(roles)]

    username = f"user_{employee.employee_id}"

    existing_user = session.query(User).filter(
        User.username == username
    ).first()

    if not existing_user:
        password_hash = hashlib.sha256(
            "password123".encode()
        ).hexdigest()

        user = User(
            employee_id=employee.employee_id,
            role_id=role.role_id,
            username=username,
            password_hash=password_hash,
            is_active=True
        )

        session.add(user)

session.commit()

print("✅ Users checked/updated!")

# -------------------------
# AUDIT LOGS
# -------------------------
from models import AuditLog, User

audit_count = session.query(AuditLog).count()
users = session.query(User).all()

action_types = [
    "CREATE",
    "UPDATE",
    "DELETE",
    "LOGIN"
]

table_names = [
    "customers",
    "products",
    "orders",
    "payments",
    "employees",
    "suppliers",
    "purchase_orders",
    "inventory_transactions"
]

for i in range(max(0, 50 - audit_count)):

    user = fake.random_element(users)
    table_name = fake.random_element(table_names)
    action_type = fake.random_element(action_types)

    audit_log = AuditLog(
        user_id=user.user_id,
        action_type=action_type,
        table_name=table_name,
        record_id=fake.random_int(min=1, max=100),
        action_time=fake.date_time_between(
            start_date="-1y",
            end_date="now"
        ),
        description=f"{action_type} action performed on {table_name}"
    )

    session.add(audit_log)

session.commit()

print("✅ Audit Logs checked/updated!")