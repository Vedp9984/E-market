import hashlib
from typing import Dict
import uuid
class User:
    def __init__(self, name: str, email: str, password: str):
        self.user_id = str(uuid.uuid4())
        self.name = name
        self.email = email
        # Hash the password for security
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.is_logged_in = False
    def login(self, password: str) -> bool:
        """Authenticate and log in a user"""
        if hashlib.sha256(password.encode()).hexdigest() == self.password:
            self.is_logged_in = True
            print(f"Welcome back, {self.name}!")
            return True
        print("Invalid login credentials.")
        return False
    def logout(self) -> None:
        """Log out a user"""
        self.is_logged_in = False
        print(f"Goodbye, {self.name}!")
    def to_dict(self) -> Dict:
        """Convert user object to dictionary for storage"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "type": self.__class__.__name__
        }
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user object from dictionary"""
        user = cls(data["name"], data["email"], "")
        user.user_id = data["user_id"]
        user.password = data["password"]  # Already hashed
        return user