from typing import List, Dict
class Discount:
    def __init__(self, discount_type: str, value: float):
        self.discount_id = str(uuid.uuid4())
        self.type = discount_type  # "percentage" or "fixed"
        self.value = value  # percentage (0-1) or fixed amount

    def apply_discount(self, price: float) -> float:
        """Apply discount to a price"""
        if self.type == "percentage":
            return price * (1 - self.value)
        elif self.type == "fixed":
            return max(price - self.value, 0)
        return price

    def to_dict(self) -> Dict:
        """Convert discount object to dictionary for storage"""
        return {
            "discount_id": self.discount_id,
            "type": self.type,
            "value": self.value
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Discount':
        """Create discount object from dictionary"""
        discount = cls(data["type"], data["value"])
        discount.discount_id = data["discount_id"]
        return discount
