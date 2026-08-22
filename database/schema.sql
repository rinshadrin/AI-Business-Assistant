CREATE DATABASE ai_business_assistant;
USE ai_business_assistant;
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);DESCRIBE customers;
INSERT INTO customers (customer_name, email, phone, city)
VALUES
('Rahul Sharma', 'rahul@gmail.com', '9876543210', 'Delhi'),
('Anjali Nair', 'anjali@gmail.com', '9876543211', 'Kochi'),
('Muhammed Rinshad', 'rinshad@gmail.com', '9876543212', 'Malappuram'),
('Arjun Menon', 'arjun@gmail.com', '9876543213', 'Bangalore'),
('Sneha Joseph', 'sneha@gmail.com', '9876543214', 'Chennai');

SELECT * FROM customers;

CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DESCRIBE suppliers;
INSERT INTO suppliers
(supplier_name, contact_person, email, phone, city)
VALUES
('Dell Technologies', 'John Smith', 'john@dell.com', '9000000001', 'Bangalore'),
('HP India', 'Rahul Gupta', 'rahul@hp.com', '9000000002', 'Mumbai'),
('Logitech', 'David Wilson', 'david@logitech.com', '9000000003', 'Chennai'),
('Samsung Electronics', 'Kim Lee', 'kim@samsung.com', '9000000004', 'Delhi'),
('Boat Lifestyle', 'Aman Verma', 'aman@boat.com', '9000000005', 'Noida');

SELECT * FROM suppliers;

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DESCRIBE categories;
INSERT INTO categories (category_name, description)
VALUES
('Laptops', 'Portable computers'),
('Accessories', 'Computer accessories'),
('Monitors', 'Display devices'),
('Storage', 'Hard disks and SSDs'),
('Networking', 'Routers and networking devices');

SELECT * FROM categories;
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category_id INT NOT NULL,
    supplier_id INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    reorder_level INT NOT NULL DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id),

    CONSTRAINT fk_product_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
);
DESCRIBE products;

INSERT INTO products
(product_name, category_id, supplier_id, unit_price, stock_quantity, reorder_level)
VALUES
('Dell Inspiron 15', 1, 1, 65000.00, 25, 10),
('HP Pavilion', 1, 2, 72000.00, 8, 10),
('Logitech Mouse', 2, 3, 799.00, 150, 30),
('Samsung SSD 1TB', 4, 4, 6500.00, 12, 15),
('Boat Wireless Earbuds', 2, 5, 2499.00, 50, 20);
SELECT * FROM products;

SELECT
    p.product_name,
    c.category_name,
    s.supplier_name
FROM products p
JOIN categories c
    ON p.category_id = c.category_id
JOIN suppliers s
    ON p.supplier_id = s.supplier_id;
    
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    order_status ENUM('Pending','Completed','Cancelled') DEFAULT 'Pending',
    total_amount DECIMAL(10,2) DEFAULT 0,

    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);
DESCRIBE orders;

INSERT INTO orders
(customer_id, order_date, order_status, total_amount)
VALUES
(1, '2026-08-01', 'Completed', 65799.00),
(2, '2026-08-02', 'Completed', 72000.00),
(3, '2026-08-02', 'Pending', 2499.00),
(4, '2026-08-03', 'Completed', 6500.00),
(5, '2026-08-03', 'Cancelled', 799.00);

SELECT * FROM orders;

SELECT
    o.order_id,
    c.customer_name,
    o.order_date,
    o.order_status,
    o.total_amount
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id;
    
    CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_orderitems_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT fk_orderitems_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

INSERT INTO order_items
(order_id, product_id, quantity, unit_price)
VALUES
(1, 1, 1, 65000.00),
(1, 3, 1, 799.00),
(2, 2, 1, 72000.00),
(3, 5, 1, 2499.00),
(4, 4, 1, 6500.00),
(5, 3, 1, 799.00);

SELECT
    o.order_id,
    c.customer_name,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS total
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN products p
    ON oi.product_id = p.product_id;
    
    CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity_in INT DEFAULT 0,
    quantity_out INT DEFAULT 0,
    transaction_date DATE NOT NULL,
    remarks VARCHAR(255),

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

INSERT INTO inventory
(product_id, quantity_in, quantity_out, transaction_date, remarks)
VALUES
(1, 50, 25, '2026-08-01', 'Laptop Sales'),
(2, 30, 22, '2026-08-02', 'HP Sales'),
(3, 200, 50, '2026-08-02', 'Mouse Sales'),
(4, 20, 8, '2026-08-03', 'SSD Sales'),
(5, 100, 50, '2026-08-03', 'Earbuds Sales');

SELECT
    p.product_name,
    i.quantity_in,
    i.quantity_out,
    (i.quantity_in - i.quantity_out) AS current_stock,
    i.transaction_date
FROM inventory i
JOIN products p
    ON i.product_id = p.product_id;
    
    SELECT * FROM inventory;
    
    DROP TABLE inventory; 
    SHOW TABLES;
    CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(50) NOT NULL,
    job_title VARCHAR(100),
    salary DECIMAL(10,2),
    hire_date DATE NOT NULL,
    employment_status ENUM('ACTIVE', 'INACTIVE', 'ON_LEAVE') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DESCRIBE employees;

INSERT INTO employees
(employee_name, email, phone, department, job_title, salary, hire_date, employment_status)
VALUES
('Arun Kumar', 'arun@erp.com', '9001000001', 'Sales', 'Sales Executive', 35000.00, '2024-01-15', 'ACTIVE'),
('Meera Nair', 'meera@erp.com', '9001000002', 'Inventory', 'Inventory Manager', 45000.00, '2023-08-10', 'ACTIVE'),
('Rahul Das', 'rahuldas@erp.com', '9001000003', 'Purchase', 'Purchase Executive', 38000.00, '2024-03-20', 'ACTIVE'),
('Aisha Khan', 'aisha@erp.com', '9001000004', 'Accounts', 'Accountant', 42000.00, '2023-11-01', 'ACTIVE'),
('Vivek Menon', 'vivek@erp.com', '9001000005', 'Admin', 'ERP Administrator', 55000.00, '2022-06-12', 'ACTIVE');

SELECT * FROM employees;

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
);

INSERT INTO roles (role_name, description)
VALUES
('Admin', 'Full access to the ERP system'),
('Manager', 'Can manage sales, purchases and inventory'),
('Sales', 'Can manage customer orders'),
('Inventory', 'Can manage stock and products'),
('Accounts', 'Can manage payments and financial records');

SELECT * FROM roles;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    role_id INT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id),

    CONSTRAINT fk_user_role
        FOREIGN KEY (role_id)
        REFERENCES roles(role_id)
);

INSERT INTO users
(employee_id, role_id, username, password_hash)
VALUES
(1, 3, 'arun', 'hashed_password_1'),
(2, 4, 'meera', 'hashed_password_2'),
(3, 2, 'rahul', 'hashed_password_3'),
(4, 5, 'aisha', 'hashed_password_4'),
(5, 1, 'vivek', 'hashed_password_5');

SELECT
    u.user_id,
    e.employee_name,
    r.role_name,
    u.username,
    u.is_active
FROM users u
JOIN employees e
    ON u.employee_id = e.employee_id
JOIN roles r
    ON u.role_id = r.role_id;
    
    CREATE TABLE inventory_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    transaction_type ENUM(
        'PURCHASE',
        'SALE',
        'CUSTOMER_RETURN',
        'SUPPLIER_RETURN',
        'ADJUSTMENT_IN',
        'ADJUSTMENT_OUT'
    ) NOT NULL,
    quantity INT NOT NULL,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    reference_type ENUM(
        'PURCHASE_ORDER',
        'CUSTOMER_ORDER',
        'MANUAL'
    ) NOT NULL,
    reference_id INT NULL,
    remarks VARCHAR(255),

    CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);
INSERT INTO inventory_transactions
(product_id, transaction_type, quantity, reference_type, reference_id, remarks)
VALUES
(1, 'PURCHASE', 50, 'PURCHASE_ORDER', 1, 'Initial stock'),
(1, 'SALE', 25, 'CUSTOMER_ORDER', 1, 'Customer purchase'),

(2, 'PURCHASE', 30, 'PURCHASE_ORDER', 2, 'Initial stock'),
(2, 'SALE', 22, 'CUSTOMER_ORDER', 2, 'Customer purchase'),

(3, 'PURCHASE', 200, 'PURCHASE_ORDER', 3, 'Initial stock'),
(3, 'SALE', 50, 'CUSTOMER_ORDER', 1, 'Customer purchase'),

(4, 'PURCHASE', 20, 'PURCHASE_ORDER', 4, 'Initial stock'),
(4, 'SALE', 8, 'CUSTOMER_ORDER', 4, 'Customer purchase'),

(5, 'PURCHASE', 100, 'PURCHASE_ORDER', 5, 'Initial stock'),
(5, 'SALE', 50, 'CUSTOMER_ORDER', 3, 'Customer purchase');


SELECT
    p.product_name,
    transaction_type,
    quantity,
    transaction_date
FROM inventory_transactions it
JOIN products p
ON it.product_id = p.product_id
ORDER BY transaction_date;

CREATE TABLE purchase_orders (
    purchase_order_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    employee_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    order_status ENUM('Pending','Received','Cancelled') DEFAULT 'Pending',
    total_amount DECIMAL(10,2) DEFAULT 0,

    CONSTRAINT fk_po_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id),

    CONSTRAINT fk_po_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees(employee_id)
);

INSERT INTO purchase_orders
(supplier_id, employee_id, purchase_date, order_status, total_amount)
VALUES
(1,3,'2026-07-25','Received',325000.00),
(2,3,'2026-07-26','Received',216000.00),
(3,2,'2026-07-27','Received',159800.00),
(4,2,'2026-07-28','Received',130000.00),
(5,3,'2026-07-29','Pending',124950.00);

SELECT
    po.purchase_order_id,
    s.supplier_name,
    e.employee_name,
    po.purchase_date,
    po.order_status,
    po.total_amount
FROM purchase_orders po
JOIN suppliers s
    ON po.supplier_id = s.supplier_id
JOIN employees e
    ON po.employee_id = e.employee_id;
    
    CREATE TABLE purchase_items (
    purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_pi_purchase_order
        FOREIGN KEY (purchase_order_id)
        REFERENCES purchase_orders(purchase_order_id),

    CONSTRAINT fk_pi_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

INSERT INTO purchase_items
(purchase_order_id, product_id, quantity, unit_price)
VALUES
(1, 1, 5, 65000.00),
(2, 2, 3, 72000.00),
(3, 3, 200, 799.00),
(4, 4, 20, 6500.00),
(5, 5, 50, 2499.00);

SELECT
    po.purchase_order_id,
    s.supplier_name,
    p.product_name,
    pi.quantity,
    pi.unit_price,
    (pi.quantity * pi.unit_price) AS total
FROM purchase_items pi
JOIN purchase_orders po
    ON pi.purchase_order_id = po.purchase_order_id
JOIN suppliers s
    ON po.supplier_id = s.supplier_id
JOIN products p
    ON pi.product_id = p.product_id;
    
    CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method ENUM(
        'Cash',
        'UPI',
        'Credit Card',
        'Debit Card',
        'Net Banking'
    ) NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_status ENUM(
        'Pending',
        'Completed',
        'Failed',
        'Refunded'
    ) DEFAULT 'Completed',

    CONSTRAINT fk_payment_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

INSERT INTO payments
(order_id, payment_method, payment_date, amount, payment_status)
VALUES
(1,'UPI','2026-08-01',65799.00,'Completed'),
(2,'Credit Card','2026-08-02',72000.00,'Completed'),
(3,'Cash','2026-08-03',2499.00,'Pending'),
(4,'Debit Card','2026-08-03',6500.00,'Completed'),
(5,'UPI','2026-08-03',799.00,'Refunded');

SELECT
    p.payment_id,
    c.customer_name,
    p.amount,
    p.payment_method,
    p.payment_status,
    p.payment_date
FROM payments p
JOIN orders o
    ON p.order_id = o.order_id
JOIN customers c
    ON o.customer_id = c.customer_id;
    
    CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id INT NOT NULL,
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255),

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);

INSERT INTO audit_logs
(user_id, action_type, table_name, record_id, description)
VALUES
(1, 'INSERT', 'orders', 1, 'Created customer order'),
(2, 'UPDATE', 'products', 3, 'Updated stock quantity'),
(3, 'INSERT', 'purchase_orders', 2, 'Created purchase order'),
(4, 'UPDATE', 'payments', 4, 'Payment status updated'),
(5, 'DELETE', 'inventory_transactions', 8, 'Removed incorrect inventory transaction');

SELECT
    a.log_id,
    u.username,
    a.action_type,
    a.table_name,
    a.record_id,
    a.action_time,
    a.description
FROM audit_logs a
JOIN users u
    ON a.user_id = u.user_id
ORDER BY a.log_id;