from typing import List, Dict
import uuid
class Payment:
    def __init__(self, order_id: str, method: str):
        self.payment_id = str(uuid.uuid4())
        self.order_id = order_id
        self.method = method
        self.status = "Pending"
    
    def process_payment(self) -> bool:
        """Process payment for an order"""
        # In a real system, this would interface with payment processors
        # Simulating payment processing
        success = True  # Assume payment succeeds
        
        if success:
            self.status = "Completed"
            print(f"Payment processed successfully for order {self.order_id}")
        else:
            self.status = "Failed"
            print(f"Payment failed for order {self.order_id}")
        
        return success
    
    def to_dict(self) -> Dict:
        """Convert payment object to dictionary for storage"""
        return {
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "method": self.method,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Payment':
        """Create payment object from dictionary"""
        payment = cls(data["order_id"], data["method"])
        payment.payment_id = data["payment_id"]
        payment.status = data["status"]
        return payment
