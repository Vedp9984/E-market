from typing import List, Dict
from customer import Customer
import uuid
import datetime

class Order:
    def __init__(self, customer: Customer, items: List[Dict], payment_method: str):
        self.order_id = str(uuid.uuid4())
        self.customer = customer
        self.items = items  # List of dicts with product_id and quantity
        self.payment_method = payment_method
        self.status = "Pending"
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.discount_applied = None
        self.payment = None
        
        self.delivery = None
        
        # Get e_store instance for calculation
        from estore import EStore
        self.total_price = self.calculate_total(EStore.get_instance())
    
    def calculate_total(self, e_store) -> float:
        """Calculate total price for order"""
        total = 0.0
        for item in self.items:
            product = e_store.get_product(item["product_id"])
            if product:
                total += product.price * item["quantity"]
        return total
    
    def apply_discount(self, discount: 'Discount') -> None:
        """Apply discount to order"""
        original_price = self.total_price
        if discount.type == "percentage":
            self.total_price *= (1 - discount.value)
        elif discount.type == "fixed":
            self.total_price -= discount.value
            if self.total_price < 0:
                self.total_price = 0
        
        self.discount_applied = discount
        print(f"Discount applied: ${original_price - self.total_price:.2f} off")
    
    def track_order(self) -> str:
        """Track order status"""
        if not self.delivery:
            return f"Order status: {self.status}"
        return f"Order status: {self.status}, Delivery status: {self.delivery.status}"
    
    def to_dict(self) -> Dict:
        """Convert order object to dictionary for storage"""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer.user_id,
            "items": self.items,
            "payment_method": self.payment_method,
            "status": self.status,
            "total_price": self.total_price,
            "date": self.date,
            "discount_applied": self.discount_applied.to_dict() if self.discount_applied else None,
            "payment_id": self.payment.payment_id if self.payment else None,
            "delivery_id": self.delivery.delivery_id if self.delivery else None
        }
