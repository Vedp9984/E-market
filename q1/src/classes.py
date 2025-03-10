import json
import os
import time
import uuid
from datetime import datetime
from enum import Enum
import random
# Enum definitions
class OrderStatus(Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    PICKED_UP = "picked_up"  # For takeaway orders
    CANCELLED = "cancelled"

class OrderType(Enum):
    DELIVERY = "delivery"
    TAKEAWAY = "takeaway"

class UserRole(Enum):
    CUSTOMER = "customer"
    DELIVERY_AGENT = "delivery_agent"
    RESTAURANT_MANAGER = "restaurant_manager"
    ADMIN = "admin"

# Data storage class
class DataStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataStore, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.data_file = "food_delivery_data.json"
        self.default_data = {
            "users": {},
            "menu_items": {},
            "orders": {},
            "delivery_agents": {}
        }
        self.data = self._load_data()
    
    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    return json.load(file)
            except Exception as e:
                print(f"Error loading data: {e}")
                return self.default_data.copy()
        return self.default_data.copy()
    
    def save_data(self):
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file, indent=2)
    
    def get_users(self):
        return self.data["users"]
    
    def get_menu_items(self):
        return self.data["menu_items"]
    
    def get_orders(self):
        return self.data["orders"]
    
    def get_delivery_agents(self):
        return self.data["delivery_agents"]

# User class
class User:
    def __init__(self, username, password, role, name=None):
        self.username = username
        self.password = password  # In a real app, this would be hashed
        self.role = role
        self.name = name if name else username
        self.id = str(uuid.uuid4())
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "role": self.role.value,
            "name": self.name
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(
            username=data["username"],
            password=data["password"],
            role=UserRole(data["role"]),
            name=data["name"]
        )
        user.id = data["id"]
        return user


class UserManager:
    def __init__(self):
        self.data_store = DataStore()
    
    def register_user(self, username, password, role, name=None):
        users = self.data_store.get_users()
        if username in users:
            return False, "Username already exists"
        
        new_user = User(username, password, role, name)
        users[username] = new_user.to_dict()
        
    
        if role == UserRole.DELIVERY_AGENT:
            delivery_agents = self.data_store.get_delivery_agents()
            delivery_agents[new_user.id] = {
                "id": new_user.id,
                "name": new_user.name,
                "status": "available",
                "current_order": None
            }
        
        self.data_store.save_data()
        return True, "User registered successfully"
    
    def authenticate(self, username, password):
        users = self.data_store.get_users()
        if username not in users:
            return False, "User not found"
        
        user_data = users[username]
        if user_data["password"] != password:
            return False, "Incorrect password"
        
        return True, User.from_dict(user_data)

# Menu item class
class MenuItem:
    def __init__(self, name, description, price, category):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.price = price
        self.category = category
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            category=data["category"]
        )
        item.id = data["id"]
        return item

# Menu management
class MenuManager:
    def __init__(self):
        self.data_store = DataStore()
    
    def add_item(self, name, description, price, category):
        menu_items = self.data_store.get_menu_items()
        new_item = MenuItem(name, description, price, category)
        menu_items[new_item.id] = new_item.to_dict()
        self.data_store.save_data()
        return new_item
    
    def update_item(self, item_id, **kwargs):
        menu_items = self.data_store.get_menu_items()
        if item_id not in menu_items:
            return False, "Item not found"
        
        for key, value in kwargs.items():
            if key in menu_items[item_id] and key != "id":
                menu_items[item_id][key] = value
        
        self.data_store.save_data()
        return True, "Item updated"
    
    def remove_item(self, item_id):
        menu_items = self.data_store.get_menu_items()
        if item_id not in menu_items:
            return False, "Item not found"
        
        del menu_items[item_id]
        self.data_store.save_data()
        return True, "Item removed"
    
    def get_all_items(self):
        return [MenuItem.from_dict(item) for item in self.data_store.get_menu_items().values()]
    
    def get_item(self, item_id):
        menu_items = self.data_store.get_menu_items()
        if item_id not in menu_items:
            return None
        return MenuItem.from_dict(menu_items[item_id])

# Order class
class Order:
    def __init__(self, customer_id, items, order_type, delivery_address=None):
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.items = items  # List of {item_id, quantity}
        self.order_type = order_type
        self.delivery_address = delivery_address
        self.status = OrderStatus.PLACED
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.estimated_delivery_time = None
        self.delivery_agent_id = None
        self.total_amount = 0
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": self.items,
            "order_type": self.order_type.value,
            "delivery_address": self.delivery_address,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "estimated_delivery_time": self.estimated_delivery_time,
            "delivery_agent_id": self.delivery_agent_id,
            "total_amount": self.total_amount
        }
    
    @classmethod
    def from_dict(cls, data):
        order = cls(
            customer_id=data["customer_id"],
            items=data["items"],
            order_type=OrderType(data["order_type"]),
            delivery_address=data["delivery_address"]
        )
        order.id = data["id"]
        order.status = OrderStatus(data["status"])
        order.created_at = data["created_at"]
        order.updated_at = data["updated_at"]
        order.estimated_delivery_time = data["estimated_delivery_time"]
        order.delivery_agent_id = data["delivery_agent_id"]
        order.total_amount = data["total_amount"]
        return order

# Order management
class OrderManager:
    def __init__(self):
        self.data_store = DataStore()
        self.menu_manager = MenuManager()
    
    def create_order(self, customer_id, items, order_type, delivery_address=None):
        # Validate order items
        menu_items = self.data_store.get_menu_items()
        valid_items = []
        total_amount = 0
        
        for item in items:
            if item["item_id"] in menu_items:
                menu_item = menu_items[item["item_id"]]
                valid_items.append({
                    "item_id": item["item_id"],
                    "name": menu_item["name"],
                    "price": menu_item["price"],
                    "quantity": item["quantity"]
                })
                total_amount += menu_item["price"] * item["quantity"]
            else:
                return False, "Item not found in menu"
        
        # Create the order
        new_order = Order(customer_id, valid_items, order_type, delivery_address)
        new_order.total_amount = total_amount
        
        # Set estimated delivery time (random for demonstration)
        prep_time = random.randint(10, 30)
        delivery_time = 0
        if order_type == OrderType.DELIVERY:
            delivery_time = random.randint(15, 45)
        total_time = prep_time + delivery_time
        
        current_time = datetime.now()
        eta = current_time.timestamp() + (total_time * 60)  # Convert minutes to seconds
        new_order.estimated_delivery_time = eta
        
        # Save order
        orders = self.data_store.get_orders()
        orders[new_order.id] = new_order.to_dict()
        self.data_store.save_data()
        
        return True, new_order
    
    def get_order(self, order_id):
        orders = self.data_store.get_orders()
        if order_id not in orders:
            return None
        return Order.from_dict(orders[order_id])
    
    def get_customer_orders(self, customer_id):
        orders = self.data_store.get_orders()
        customer_orders = []
        
        for order_data in orders.values():
            if order_data["customer_id"] == customer_id:
                customer_orders.append(Order.from_dict(order_data))
        
        return customer_orders
    
    def update_order_status(self, order_id, new_status, delivery_agent_id=None):
        orders = self.data_store.get_orders()
        if order_id not in orders:
            return False, "Order not found"
        
        orders[order_id]["status"] = new_status.value
        orders[order_id]["updated_at"] = datetime.now().isoformat()
        
        if delivery_agent_id:
            orders[order_id]["delivery_agent_id"] = delivery_agent_id
            
            # Update delivery agent status
            delivery_agents = self.data_store.get_delivery_agents()
            if delivery_agent_id in delivery_agents:
                delivery_agents[delivery_agent_id]["status"] = "busy"
                delivery_agents[delivery_agent_id]["current_order"] = order_id
        
        # If delivered/picked up, release the delivery agent
        if new_status in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP]:
            current_agent_id = orders[order_id]["delivery_agent_id"]
            if current_agent_id:
                delivery_agents = self.data_store.get_delivery_agents()
                if current_agent_id in delivery_agents:
                    delivery_agents[current_agent_id]["status"] = "available"
                    delivery_agents[current_agent_id]["current_order"] = None
        
        self.data_store.save_data()
        return True, "Order status updated"
    
    def get_all_orders(self):
        return [Order.from_dict(order) for order in self.data_store.get_orders().values()]
    
    def get_time_remaining(self, order_id):
        order = self.get_order(order_id)
        if not order or not order.estimated_delivery_time:
            return None
        
        current_time = datetime.now().timestamp()
        remaining_seconds = max(0, order.estimated_delivery_time - current_time)
        return int(remaining_seconds / 60)  # Return minutes

# Delivery management
class DeliveryManager:
    def __init__(self):
        self.data_store = DataStore()
    
    def get_available_agents(self):
        delivery_agents = self.data_store.get_delivery_agents()
        return [agent for agent in delivery_agents.values() if agent["status"] == "available"]
    
    def assign_delivery_agent(self, order_id):
        available_agents = self.get_available_agents()
        orders = self.data_store.get_orders()
        
        if order_id not in orders:
            return False, "Order not found"
        
        if not available_agents:
            return False, "No delivery agents available"
        
        # Choose a random agent for simplicity
        agent = random.choice(available_agents)
        orders[order_id]["delivery_agent_id"] = agent["id"]
        
        # Update agent status
        delivery_agents = self.data_store.get_delivery_agents()
        delivery_agents[agent["id"]]["status"] = "busy"
        delivery_agents[agent["id"]]["current_order"] = order_id
        
        self.data_store.save_data()
        return True, agent["id"]
    
    def get_agent_orders(self, agent_id):
        orders = self.data_store.get_orders()
        agent_orders = []
        
        for order_data in orders.values():
            if order_data["delivery_agent_id"] == agent_id:
                agent_orders.append(Order.from_dict(order_data))
        
        return agent_orders
