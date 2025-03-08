from typing import Dict
import uuid

class Product:
    def __init__(self, name: str, category: str, price: float, stock: int):
        self.product_id = str(uuid.uuid4())
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
    
    def update_stock(self, quantity_change: int) -> None:
        """Update product stock (positive for increase, negative for decrease)"""
        self.stock += quantity_change
        if self.stock < 0:
            self.stock = 0
    
    def apply_discount(self, discount_percentage: float) -> float:
        """Apply discount to product price"""
        return self.price * (1 - discount_percentage)
    
    def to_dict(self) -> Dict:
        """Convert product object to dictionary for storage"""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Product':
        """Create product object from dictionary"""
        product = cls(data["name"], data["category"], data["price"], data["stock"])
        product.product_id = data["product_id"]
        return product
