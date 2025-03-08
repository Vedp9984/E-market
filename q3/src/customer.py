from user import User
from typing import Dict, List, Optional
class Customer(User):
    def __init__(self, name: str, email: str, password: str):
        super().__init__(name, email, password)
        self.order_history = []

    def place_order(self, e_store: 'EStore', items: List[Dict], payment_method: str) -> Optional['Order']:
        """Place a new order"""
        if not self.is_logged_in:
            print("Please log in to place an order.")
            return None

        # Validate items are in stock
        for item in items:
            product = e_store.get_product(item["product_id"])
            if not product:
                print(f"Product with ID {item['product_id']} not found.")
                return None
            if product.stock < item["quantity"]:
                print(f"Insufficient stock for {product.name}. Available: {product.stock}")
                return None

        # Create order
        order = Order(self, items, payment_method)

        # Update stock
        for item in items:
            product = e_store.get_product(item["product_id"])
            product.update_stock(-item["quantity"])

        # Add to order history
        self.order_history.append(order.order_id)

        # Process order in e-store
        e_store.process_order(order)

        print(f"Order placed successfully! Your order ID is: {order.order_id}")
        return order

    def view_order_history(self, e_store: 'EStore') -> None:
        """View customer's order history"""
        if not self.is_logged_in:
            print("Please log in to view order history.")
            return

        if not self.order_history:
            print("You haven't placed any orders yet.")
            return

        print("\n==== Your Order History ====")
        for order_id in self.order_history:
            order = e_store.get_order(order_id)
            if order:
                print(f"Order ID: {order.order_id}")
                print(f"Date: {order.date}")
                print(f"Status: {order.status}")
                print(f"Total: ${order.total_price:.2f}")
                print("------------------------")

    def get_discount(self) -> float:
        """Get customer's discount percentage"""
        # Basic implementation - could be expanded based on loyalty, etc.
        return 0.05  # 5% discount

    def to_dict(self) -> Dict:
        """Convert customer object to dictionary for storage"""
        data = super().to_dict()
        data["order_history"] = self.order_history
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'Customer':
        """Create customer object from dictionary"""
        customer = super(Customer, cls).from_dict(data)
        customer.order_history = data.get("order_history", [])
        return customer