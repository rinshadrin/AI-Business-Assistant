from db import SessionLocal
from models import Customer


def get_all_customers():
    session = SessionLocal()

    try:
        customers = session.query(Customer).all()

        for customer in customers:
            print(
                customer.customer_id,
                customer.customer_name,
                customer.email,
                customer.phone,
                customer.city
            )

    finally:
        session.close()


if __name__ == "__main__":
    get_all_customers()


def add_customer():
    session = SessionLocal()

    new_customer = Customer(
        customer_name="Akhil Kumar",
        email="akhil@gmail.com",
        phone="9876543220",
        city="Thrissur"
    )

    session.add(new_customer)
    session.commit()

    print("Customer Added Successfully!")

    session.close()

if __name__ == "__main__":
    add_customer()

def update_customer():
    session = SessionLocal()

    customer = session.query(Customer).filter_by(customer_id=6).first()

    if customer:
        customer.city = "Kozhikode"
        customer.phone = "9999999999"

        session.commit()
        print("Customer Updated Successfully!")
    else:
        print("Customer Not Found!")

    session.close()


if __name__ == "__main__":
    update_customer()
