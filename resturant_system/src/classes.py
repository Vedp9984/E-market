import time
import random
import sqlite3
import json
from enum import Enum
from datetime import datetime, timedelta  # Make sure timedelta is imported
import uuid
import os
from datetime import datetime

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
        self.db_file = "food_delivery.db"
        # Connect with check_same_thread=False to allow access from multiple threads
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        # Cache loaded data to maintain compatibility with existing code
        self.data = self._load_data()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            name TEXT
        )
        ''')
        
        # Create menu_items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            price REAL,
            category TEXT
        )
        ''')
        
        # Create orders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_id TEXT,
            order_type TEXT,
            delivery_address TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            estimated_delivery_time TEXT,
            delivery_agent_id TEXT,
            total_amount REAL,
            items TEXT  -- JSON string of items
        )
        ''')
        
        # Create delivery_agents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_agents (
            id TEXT PRIMARY KEY,
            name TEXT,
            status TEXT,
            current_order TEXT
        )
        ''')
        
        self.conn.commit()
    
    def _load_data(self):
        """Load data from SQLite into our in-memory data structure for compatibility"""
        data = {
            "users": {},
            "menu_items": {},
            "orders": {},
            "delivery_agents": {}
        }
        
        cursor = self.conn.cursor()
        
        # Load users
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            row_dict = dict(row)
            username = row_dict.pop("username")
            # Include username in the user data
            row_dict["username"] = username  # Add this line
            data["users"][username] = row_dict
        
        # Load menu_items
        cursor.execute("SELECT * FROM menu_items")
        rows = cursor.fetchall()
        for row in rows:
            row_dict = dict(row)
            data["menu_items"][row_dict["id"]] = row_dict
        
        # Load orders
        cursor.execute("SELECT * FROM orders")
        rows = cursor.fetchall()
        for row in rows:
            row_dict = dict(row)
            row_dict["items"] = json.loads(row_dict["items"])
            data["orders"][row_dict["id"]] = row_dict
        
        # Load delivery_agents
        cursor.execute("SELECT * FROM delivery_agents")
        rows = cursor.fetchall()
        for row in rows:
            row_dict = dict(row)
            data["delivery_agents"][row_dict["id"]] = row_dict
        
        return data
    
    def save_data(self):
        """Save in-memory data to SQLite database"""
        # Get a new cursor for this transaction
        cursor = self.conn.cursor()
        
        try:
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Save users: First delete existing then insert new
            cursor.execute("DELETE FROM users")
            for username, user_data in self.data["users"].items():
                cursor.execute(
                    "INSERT INTO users (id, username, password, role, name) VALUES (?, ?, ?, ?, ?)",
                    (user_data["id"], username, user_data["password"], user_data["role"], user_data["name"])
                )
            
            # Save menu_items: First delete existing then insert new
            cursor.execute("DELETE FROM menu_items")
            for item_id, item_data in self.data["menu_items"].items():
                cursor.execute(
                    "INSERT INTO menu_items (id, name, description, price, category) VALUES (?, ?, ?, ?, ?)",
                    (item_id, item_data["name"], item_data["description"], item_data["price"], item_data["category"])
                )
            
            # Save orders: First delete existing then insert new
            cursor.execute("DELETE FROM orders")
            for order_id, order_data in self.data["orders"].items():
                # Convert items to JSON string
                items_json = json.dumps(order_data["items"])
                
                # Handle any None values properly
                delivery_address = order_data.get("delivery_address")
                delivery_agent_id = order_data.get("delivery_agent_id")
                
                cursor.execute(
                    """INSERT INTO orders 
                       (id, customer_id, order_type, delivery_address, status, created_at, 
                        updated_at, estimated_delivery_time, delivery_agent_id, total_amount, items)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        order_id, order_data["customer_id"], order_data["order_type"],
                        delivery_address, order_data["status"], 
                        order_data["created_at"], order_data["updated_at"],
                        order_data["estimated_delivery_time"], delivery_agent_id,
                        order_data["total_amount"], items_json
                    )
                )
            
            # Save delivery_agents: First delete existing then insert new
            cursor.execute("DELETE FROM delivery_agents")
            for agent_id, agent_data in self.data["delivery_agents"].items():
                cursor.execute(
                    "INSERT INTO delivery_agents (id, name, status, current_order) VALUES (?, ?, ?, ?)",
                    (agent_id, agent_data["name"], agent_data.get("status", "available"), agent_data.get("current_order"))
                )
            
            # Commit the transaction
            self.conn.commit()
        except Exception as e:
            # Rollback on error
            self.conn.rollback()
            print(f"Error saving data to SQLite: {e}")
    
    def get_users(self):
        # First refresh data from database to get latest changes
        self.data = self._load_data()
        return self.data["users"]
    
    def get_menu_items(self):
        # First refresh data from database to get latest changes
        self.data = self._load_data()
        return self.data["menu_items"]
    
    def get_orders(self):
        # First refresh data from database to get latest changes
        self.data = self._load_data()
        return self.data["orders"]
    
    def get_delivery_agents(self):
        # First refresh data from database to get latest changes
        self.data = self._load_data()
        return self.data["delivery_agents"]
    
    def close(self):
        if hasattr(self, 'conn'):
            self.conn.close()
         
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
        # Ensure role is converted to UserRole enum if it's a string
        role = data["role"]
        if isinstance(role, str):
            role = UserRole(role)
        
        user = cls(
            username=data["username"],
            password=data["password"],
            role=role,
            name=data["name"]
        )
        user.id = data["id"]
        return user


# Changes to the UserManager class in classes.py

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
        
        # Make sure username is included in the user_data
        if "username" not in user_data:
            user_data["username"] = username
        
        if user_data["password"] != password:
            return False, "Incorrect password"
        
        try:
            # Convert string role to enum if needed
            role = user_data.get("role")
            if isinstance(role, str):
                # Handle both direct enum name and enum value cases
                try:
                    role = UserRole(role)
                except ValueError:
                    # If direct conversion fails, try mapping to enum
                    role_map = {
                        "customer": UserRole.CUSTOMER,
                        "restaurant_manager": UserRole.RESTAURANT_MANAGER,
                        "delivery_agent": UserRole.DELIVERY_AGENT,
                        "admin": UserRole.ADMIN
                    }
                    role = role_map.get(role.lower(), UserRole.CUSTOMER)
            
            user = User(
                username=user_data["username"], 
                password=user_data["password"],
                role=role,
                name=user_data.get("name", username)
            )
            
            # Make sure the ID is set
            user.id = user_data.get("id", str(uuid.uuid4()))
            
            return True, user
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False, f"Authentication error: {str(e)}"

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
        self.items = items
        self.order_type = order_type
        self.delivery_address = delivery_address
        self.status = OrderStatus.PLACED
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at
        
        # Store as float for consistent comparisons
        self.estimated_delivery_time = (datetime.now() + timedelta(minutes=60)).timestamp()
        
        self.delivery_agent_id = None
        
        # Calculate total amount
        self.total_amount = sum(item["price"] * item["quantity"] for item in items) if items else 0
    
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
        """Update the status of an order and handle agent assignments"""
        orders = self.data_store.get_orders()
        
        if order_id not in orders:
            return False, "Order not found"
        
        # Update order status - save the enum value
        orders[order_id]["status"] = new_status.value
        orders[order_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # If a delivery agent is specified, update the delivery agent info
        if delivery_agent_id:
            orders[order_id]["delivery_agent_id"] = delivery_agent_id
            
            # Update delivery agent status
            delivery_agents = self.data_store.get_delivery_agents()
            if delivery_agent_id in delivery_agents:
                delivery_agents[delivery_agent_id]["status"] = "busy"
                delivery_agents[delivery_agent_id]["current_order"] = order_id
        
        # If delivered/picked up/cancelled, release the delivery agent
        if new_status in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP, OrderStatus.CANCELLED]:
            agent_id = orders[order_id].get("delivery_agent_id")
            if agent_id:
                delivery_agents = self.data_store.get_delivery_agents()
                if agent_id in delivery_agents:
                    delivery_agents[agent_id]["status"] = "available"
                    delivery_agents[agent_id]["current_order"] = None
        
        # Save changes
        self.data_store.save_data()
        
        return True, "Order status updated successfully"
        
    def get_all_orders(self):
        return [Order.from_dict(order) for order in self.data_store.get_orders().values()]
            
        # Make sure the get_time_remaining method is properly indented as part of OrderManager
  
        
    def get_time_remaining(self, order_id):
        order = self.get_order(order_id)
        if not order:
            return None
        
        current_time = datetime.now().timestamp()
        
        # Convert estimated_delivery_time to float if it's a string
        if isinstance(order.estimated_delivery_time, str):
            try:
                estimated_delivery_time = float(order.estimated_delivery_time)
            except (ValueError, TypeError):
                # Handle the case where conversion fails
                return 0
        else:
            estimated_delivery_time = order.estimated_delivery_time
        
        remaining_seconds = max(0, estimated_delivery_time - current_time)
        remaining_minutes = int(remaining_seconds / 60)
        
        return remaining_minutes
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
        """Get all orders assigned to a specific delivery agent"""
        # Make sure to refresh data from database
        self.data_store.data = self.data_store._load_data()
        
        # Print the agent ID for debugging
        print(f"Looking for orders for agent ID: {agent_id}")
        
        orders = self.data_store.get_orders()
        agent_orders = []
        
        for order_id, order_data in orders.items():
            # Debug the order's delivery_agent_id
            delivery_agent_id = order_data.get("delivery_agent_id")
            print(f"Order {order_id} has agent: {delivery_agent_id}")
            
            # The problem might be in the order update function
            # Let's try a more lenient comparison
            if delivery_agent_id is not None and str(delivery_agent_id) == str(agent_id):
                agent_orders.append(Order.from_dict(order_data))
        
        # Debug the final result
        print(f"Found {len(agent_orders)} orders for agent {agent_id}")
        
        return agent_orders
