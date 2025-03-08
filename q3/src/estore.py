
# --- Main E-Store System ---
from typing import List, Dict, Optional
import os
import json
import datetime
from product import Product
from admin import Admin
from customer import Customer
from retail_store import RetailStore
from order import Order
from discount import Discount
from payment import Payment
from delivery import Delivery
from user import User
class EStore:
    _instance = None

    @classmethod
    def get_instance(cls) -> 'EStore':
        """Singleton pattern to ensure only one EStore instance exists"""
        if cls._instance is None:
            cls._instance = EStore()    
        return cls._instance

    def __init__(self):
        if EStore._instance is not None:
            raise Exception("This class is a singleton! Use get_instance() instead.")

        self.users = []
        self.products = []
        self.orders = []
        self.discounts = []
        self.payments = []
        self.deliveries = []
        self.retail_stores = []  # Add this line
        # Create default admin user
        admin = Admin("Admin", "admin@dollmart.com", "admin123")
        self.users.append(admin)
        # Load data if it exists
        self.load_data()
    def search_product(self, query: str) -> List[Product]:
        """Search for products by name or category"""
        query = query.lower()
        results = []
        for product in self.products:
            if query in product.name.lower() or query in product.category.lower():
                results.append(product)
        return results

    def add_product(self, product: Product) -> None:
        """Add a new product to the store"""
        self.products.append(product)
        self.save_data()

    def get_product(self, product_id: str) -> Optional[Product]:
        """Get a product by ID"""
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None

    def delete_product(self, product_id: str) -> bool:
        """Delete a product by ID"""
        for i, product in enumerate(self.products):
            if product.product_id == product_id:
                del self.products[i]
                self.save_data()
                return True
        return False

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID"""
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def process_order(self, order: Order) -> None:
        """Process a new order"""
        # Create payment
        payment = Payment(order.order_id, order.payment_method)
        self.payments.append(payment)
        order.payment = payment

        # Process payment
        if payment.process_payment():
            order.status = "Confirmed"

            # Create delivery
            delivery_date = datetime.datetime.now() + datetime.timedelta(days=3)
            delivery = Delivery(order.order_id, delivery_date.strftime("%Y-%m-%d"))
            self.deliveries.append(delivery)
            order.delivery = delivery
        else:
            order.status = "Payment Failed"

        # Add order to the system
        self.orders.append(order)
        self.save_data()

    def get_user(self, email: str) -> Optional[User]:
        """Get a user by email"""
        for user in self.users:
            if user.email == email:
                return user
        return None

    def add_user(self, user: User) -> None:
        """Add a new user to the system"""
        self.users.append(user)
        self.save_data()

    def save_data(self) -> None:
        """Save data to files"""
        os.makedirs("data", exist_ok=True)

        # Save users
        with open("data/users.json", "w") as f:
            users_data = [user.to_dict() for user in self.users]
            json.dump(users_data, f, indent=4)

        # Save products
        with open("data/products.json", "w") as f:
            products_data = [product.to_dict() for product in self.products]
            json.dump(products_data, f, indent=4)

        # Save orders (simplified to avoid circular references)
        with open("data/orders.json", "w") as f:
            orders_data = [order.to_dict() for order in self.orders]
            json.dump(orders_data, f, indent=4)

        # Save payments
        with open("data/payments.json", "w") as f:
            payments_data = [payment.to_dict() for payment in self.payments]
            json.dump(payments_data, f, indent=4)

        # Save deliveries
        with open("data/deliveries.json", "w") as f:
            deliveries_data = [delivery.to_dict() for delivery in self.deliveries]
            json.dump(deliveries_data, f, indent=4)

        # Save discounts
        with open("data/discounts.json", "w") as f:
            discounts_data = [discount.to_dict() for discount in self.discounts]
            json.dump(discounts_data, f, indent=4)

    def load_data(self) -> None:
        """Load data from files"""
        if not os.path.exists("data"):
            return

        # Load products
        if os.path.exists("data/products.json"):
            with open("data/products.json", "r") as f:
                try:
                    products_data = json.load(f)
                    self.products = [Product.from_dict(data) for data in products_data]
                except json.JSONDecodeError:
                    pass

        # Load users
        if os.path.exists("data/users.json"):
            with open("data/users.json", "r") as f:
                try:
                    users_data = json.load(f)
                    self.users = []
                    self.retail_stores = []
                    for data in users_data:
                        user_type = data.get("type", "User")
                        if user_type == "Customer":
                            self.users.append(Customer.from_dict(data))
                        elif user_type == "RetailStore":
                            retail_store = RetailStore.from_dict(data)
                            self.users.append(retail_store)
                            self.retail_stores.append(retail_store)
                        elif user_type == "Admin":
                            self.users.append(Admin.from_dict(data))
                        else:
                            self.users.append(User.from_dict(data))
                except json.JSONDecodeError:
                    pass

        # Load discounts
        if os.path.exists("data/discounts.json"):
            with open("data/discounts.json", "r") as f:
                try:
                    discounts_data = json.load(f)
                    self.discounts = [Discount.from_dict(data) for data in discounts_data]
                except json.JSONDecodeError:
                    pass

        # Load payments
        if os.path.exists("data/payments.json"):
            with open("data/payments.json", "r") as f:
                try:
                    payments_data = json.load(f)
                    self.payments = [Payment.from_dict(data) for data in payments_data]
                except json.JSONDecodeError:
                    pass

        # Load deliveries
        if os.path.exists("data/deliveries.json"):
            with open("data/deliveries.json", "r") as f:
                try:
                    deliveries_data = json.load(f)
                    self.deliveries = [Delivery.from_dict(data) for data in deliveries_data]
                except json.JSONDecodeError:
                    pass

        # Load orders (partial load due to object references)
        if os.path.exists("data/orders.json"):
            with open("data/orders.json", "r") as f:
                try:
                    orders_data = json.load(f)
                    for data in orders_data:
                        # Find customer by ID
                        customer = None
                        for user in self.users:
                            if isinstance(user, Customer) and user.user_id == data["customer_id"]:
                                customer = user
                                break

                        if customer:
                            # Create order with minimal data
                            order = Order.__new__(Order)
                            order.customer = customer
                            order.items = data["items"]
                            order.payment_method = data["payment_method"]
                            order.order_id = data["order_id"]
                            order.status = data["status"]
                            order.total_price = data["total_price"]  # Use saved value instead of recalculating
                            order.date = data["date"]
                            order.discount_applied = None
                            order.payment = None
                            order.delivery = None

                            # Link to payment
                            if data["payment_id"]:
                                for payment in self.payments:
                                    if payment.payment_id == data["payment_id"]:
                                        order.payment = payment
                                        break

                            # Link to delivery
                            if data["delivery_id"]:
                                for delivery in self.deliveries:
                                    if delivery.delivery_id == data["delivery_id"]:
                                        order.delivery = delivery
                                        break

                            self.orders.append(order)
                except json.JSONDecodeError:
                    pass