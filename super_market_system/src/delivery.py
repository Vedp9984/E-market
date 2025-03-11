from typing import List, Dict
import uuid
class Delivery:
    def __init__(self, order_id: str, expected_date: str):
        self.delivery_id = str(uuid.uuid4())
        self.order_id = order_id
        self.status = "Processing"
        self.expected_date = expected_date
    
    def update_status(self, new_status: str) -> None:
        """Update delivery status"""
        valid_statuses = ["Processing", "Shipped", "Out for Delivery", "Delivered"]
        if new_status in valid_statuses:
            self.status = new_status
            print(f"Delivery status updated to: {new_status}")
        else:
            print(f"Invalid status. Valid statuses are: {', '.join(valid_statuses)}")
    
    def to_dict(self) -> Dict:
        """Convert delivery object to dictionary for storage"""
        return {
            "delivery_id": self.delivery_id,
            "order_id": self.order_id,
            "status": self.status,
            "expected_date": self.expected_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Delivery':
        """Create delivery object from dictionary"""
        delivery = cls(data["order_id"], data["expected_date"])
        delivery.delivery_id = data["delivery_id"]
        delivery.status = data["status"]
        return delivery
