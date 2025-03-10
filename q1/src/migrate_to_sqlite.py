import json
import os
import sqlite3

def migrate_json_to_sqlite():
    # Path to your JSON file
    json_file = "food_delivery_data.json"
    db_file = "food_delivery.db"
    
    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"JSON file {json_file} not found.")
        return False
    
    try:
        # Load JSON data
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Connect to SQLite
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            name TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            price REAL,
            category TEXT
        )
        ''')
        
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
            items TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_agents (
            id TEXT PRIMARY KEY,
            name TEXT,
            status TEXT,
            current_order TEXT
        )
        ''')
        
        # Migrate users
        for username, user_data in data.get("users", {}).items():
            try:
                cursor.execute(
                    "INSERT INTO users (id, username, password, role, name) VALUES (?, ?, ?, ?, ?)",
                    (user_data.get("id", ""), username, user_data.get("password", ""), 
                     user_data.get("role", ""), user_data.get("name", ""))
                )
            except sqlite3.IntegrityError:
                print(f"Skipping duplicate user: {username}")
        
        # Migrate menu items
        for item_id, item_data in data.get("menu_items", {}).items():
            try:
                cursor.execute(
                    "INSERT INTO menu_items (id, name, description, price, category) VALUES (?, ?, ?, ?, ?)",
                    (item_id, item_data.get("name", ""), item_data.get("description", ""), 
                     item_data.get("price", 0), item_data.get("category", ""))
                )
            except sqlite3.IntegrityError:
                print(f"Skipping duplicate menu item: {item_id}")
        
        # Migrate orders
        for order_id, order_data in data.get("orders", {}).items():
            try:
                # Convert items to JSON string
                items_json = json.dumps(order_data.get("items", []))
                
                cursor.execute(
                    """INSERT INTO orders 
                       (id, customer_id, order_type, delivery_address, status, created_at, 
                        updated_at, estimated_delivery_time, delivery_agent_id, total_amount, items)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (order_id, order_data.get("customer_id", ""), order_data.get("order_type", ""),
                     order_data.get("delivery_address"), order_data.get("status", ""), 
                     order_data.get("created_at", ""), order_data.get("updated_at", ""),
                     order_data.get("estimated_delivery_time", ""), order_data.get("delivery_agent_id"),
                     order_data.get("total_amount", 0), items_json)
                )
            except sqlite3.IntegrityError:
                print(f"Skipping duplicate order: {order_id}")
        
        # Migrate delivery agents
        for agent_id, agent_data in data.get("delivery_agents", {}).items():
            try:
                cursor.execute(
                    "INSERT INTO delivery_agents (id, name, status, current_order) VALUES (?, ?, ?, ?)",
                    (agent_id, agent_data.get("name", ""), agent_data.get("status", "available"), 
                     agent_data.get("current_order"))
                )
            except sqlite3.IntegrityError:
                print(f"Skipping duplicate delivery agent: {agent_id}")
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"Migration completed successfully. Data migrated to {db_file}")
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    migrate_json_to_sqlite()