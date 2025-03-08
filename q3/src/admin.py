from user import User
from typing import List, Dict

class Admin(User):
    def __init__(self, name: str, email: str, password: str):
        super().__init__(name, email, password)

    def view_orders(self, e_store: 'EStore') -> None:
        """View all orders"""
        if not self.is_logged_in:
            print("Please log in as admin to view orders.")
            return

        orders = e_store.orders
        if not orders:
            print("No orders available.")
            return

        print("\n==== All Orders ====")
        for order in orders:
            print(f"Order ID: {order.order_id}")
            print(f"Customer: {order.customer.name}")
            print(f"Date: {order.date}")
            print(f"Status: {order.status}")
            print(f"Total: ${order.total_price:.2f}")
            print("Items:")
            for item in order.items:
                product = e_store.get_product(item["product_id"])
                if product:
                    print(f"  - {item['quantity']}x {product.name} (${product.price:.2f} each)")
            print("------------------------")

    def view_retail_stores(self, e_store: 'EStore') -> None:
        """View all retail stores in the e-store"""
        if not self.is_logged_in:
            print("Please log in as admin to view retail stores.")
            return

        retail_stores = e_store.retail_stores
        if not retail_stores:
            print("No retail stores available.")
            return

        print("\n==== All Retail Stores ====")
        for store in retail_stores:
            print(f"Store ID: {store.business_id}")
            print(f"Name: {store.store_name}")
            print(f"Owner: {store.name}")
            print("------------------------")