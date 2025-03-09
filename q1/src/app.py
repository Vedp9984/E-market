
from classes import User, UserRole, MenuItem, Order, OrderStatus, OrderType, UserManager,DataStore,MenuManager,OrderManager,DeliveryManager,Order
from datetime import datetime, timezone
# CLI Interface
class FoodDeliveryApp:
    def __init__(self):
        self.user_manager = UserManager()
        self.menu_manager = MenuManager()
        self.order_manager = OrderManager()
        self.delivery_manager = DeliveryManager()
        self.current_user = None
        
        # Initialize with sample data if empty
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        data_store = DataStore()
        
        # Add sample menu items if none exist
        if not data_store.get_menu_items():
            self.menu_manager.add_item("Margherita Pizza", "Classic cheese and tomato pizza", 12.99, "Pizza")
            self.menu_manager.add_item("Pepperoni Pizza", "Pizza with pepperoni toppings", 14.99, "Pizza")
            self.menu_manager.add_item("Chicken Burger", "Grilled chicken burger with lettuce and mayo", 9.99, "Burger")
            self.menu_manager.add_item("Vegetable Biryani", "Fragrant rice dish with mixed vegetables", 10.99, "Main")
            self.menu_manager.add_item("Chocolate Brownie", "Rich chocolate brownie with ice cream", 6.99, "Dessert")
        
        # Add sample users if none exist
        if not data_store.get_users():
            self.user_manager.register_user("customer1", "pass123", UserRole.CUSTOMER, "John Doe")
            self.user_manager.register_user("manager1", "pass123", UserRole.RESTAURANT_MANAGER, "Restaurant Manager")
            self.user_manager.register_user("agent1", "pass123", UserRole.DELIVERY_AGENT, "Delivery Agent 1")
            self.user_manager.register_user("admin1", "pass123", UserRole.ADMIN, "System Admin")
    
    def start(self):
        print("===== Welcome to Food Delivery System =====")
        while True:
            if not self.current_user:
                self._show_auth_menu()
            else:
                if self.current_user.role == UserRole.CUSTOMER:
                    self._show_customer_menu()
                elif self.current_user.role == UserRole.RESTAURANT_MANAGER:
                    self._show_manager_menu()
                elif self.current_user.role == UserRole.DELIVERY_AGENT:
                    self._show_delivery_agent_menu()
                elif self.current_user.role == UserRole.ADMIN:
                    self._show_admin_menu()
    
    def _show_auth_menu(self):
        print("\n1. Login")
        print("2. Register as Customer")
        print("3. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            self._login()
        elif choice == "2":
            self._register_customer()
        elif choice == "3":
            print("Thank you for using Food Delivery System!")
            exit(0)
        else:
            print("Invalid choice. Please try again.")
    
    def _login(self):
        username = input("Username: ")
        password = input("Password: ")
        
        success, result = self.user_manager.authenticate(username, password)
        if success:
            self.current_user = result
            print(f"Welcome, {self.current_user.name}!")
        else:
            print(f"Login failed: {result}")
    
    def _register_customer(self):
        username = input("Username: ")
        password = input("Password: ")
        name = input("Full Name: ")
        
        success, message = self.user_manager.register_user(username, password, UserRole.CUSTOMER, name)
        print(message)
    
    def _show_customer_menu(self):
        print(f"\n===== Customer Menu ({self.current_user.name}) =====")
        print("1. View Menu")
        print("2. Place Order")
        print("3. View My Orders")
        print("4. Track Order")
        print("5. Logout")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            self._display_menu()
        elif choice == "2":
            self._place_order()
        elif choice == "3":
            self._view_customer_orders()
        elif choice == "4":
            self._track_order()
        elif choice == "5":
            self.current_user = None
            print("Logged out successfully.")
        else:
            print("Invalid choice. Please try again.")
    
    def _show_manager_menu(self):
        print(f"\n===== Restaurant Manager Menu ({self.current_user.name}) =====")
        print("1. View All Orders")
        print("2. Update Order Status")
        print("3. Manage Menu")
        print("4. Logout")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            self._view_all_orders()
        elif choice == "2":
            self._update_order_status()
        elif choice == "3":
            self._manage_menu()
        elif choice == "4":
            self.current_user = None
            print("Logged out successfully.")
        else:
            print("Invalid choice. Please try again.")
    
    def _show_delivery_agent_menu(self):
        print(f"\n===== Delivery Agent Menu ({self.current_user.name}) =====")
        print("1. View My Assigned Orders")
        print("2. Update Delivery Status")
        print("3. Logout")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            self._view_agent_orders()
        elif choice == "2":
            self._update_delivery_status()
        elif choice == "3":
            self.current_user = None
            print("Logged out successfully.")
        else:
            print("Invalid choice. Please try again.")
    
    def _show_admin_menu(self):
        print(f"\n===== Admin Menu ({self.current_user.name}) =====")
        print("1. View All Orders")
        print("2. View All Delivery Agents")
        print("3. Register New Staff")
        print("4. Logout")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            self._view_all_orders()
        elif choice == "2":
            self._view_all_agents()
        elif choice == "3":
            self._register_staff()
        elif choice == "4":
            self.current_user = None
            print("Logged out successfully.")
        else:
            print("Invalid choice. Please try again.")
    
    def _display_menu(self):
        print("\n===== Menu =====")
        menu_items = self.menu_manager.get_all_items()
        
        current_category = None
        for item in sorted(menu_items, key=lambda x: x.category):
            if item.category != current_category:
                current_category = item.category
                print(f"\n--- {current_category} ---")
            
            print(f"{item.id}: {item.name} - ${item.price:.2f}")
            print(f"   {item.description}")
        
        input("\nPress Enter to continue...")
    
    def _place_order(self):
        print("\n===== Place Order =====")
        
        # Display menu for selection
        self._display_menu()
        
        cart = []
        while True:
            item_id = input("\nEnter item ID to add to cart (or 'done' to finish): ")
            if item_id.lower() == 'done':
                break
            
            item = self.menu_manager.get_item(item_id)
            if not item:
                print("Item not found. Please try again.")
                continue
            
            try:
                quantity = int(input(f"Enter quantity for {item.name}: "))
                if quantity <= 0:
                    print("Quantity must be positive.")
                    continue
                
                cart.append({"item_id": item_id, "quantity": quantity})
                print(f"{quantity}x {item.name} added to cart.")
            except ValueError:
                print("Invalid quantity. Please enter a number.")
        
        if not cart:
            print("Cart is empty. Order cancelled.")
            return
        
        # Choose order type
        print("\nOrder Type:")
        print("1. Home Delivery")
        print("2. Takeaway")
        order_type_choice = input("Enter your choice: ")
        
        delivery_address = None
        order_type = None
        
        if order_type_choice == "1":
            order_type = OrderType.DELIVERY
            delivery_address = input("Enter delivery address: ")
        elif order_type_choice == "2":
            order_type = OrderType.TAKEAWAY
        else:
            print("Invalid choice. Order cancelled.")
            return
        
        # Create the order
        success, result = self.order_manager.create_order(
            self.current_user.id,
            cart,
            order_type,
            delivery_address
        )
        
        if success:
            order = result
            print(f"\nOrder placed successfully!")
            print(f"Order ID: {order.id}")
            print(f"Total amount: ${order.total_amount:.2f}")
            
            # Assign delivery agent if it's a delivery order
            if order_type == OrderType.DELIVERY:
                success, agent_id = self.delivery_manager.assign_delivery_agent(order.id)
                if success:
                    print("Delivery agent assigned.")
                else:
                    print(f"Note: {agent_id}")
            
            time_remaining = self.order_manager.get_time_remaining(order.id)
            if time_remaining:
                if order_type == OrderType.DELIVERY:
                    print(f"Estimated delivery time: {time_remaining} minutes")
                else:
                    print(f"Estimated pickup time: {time_remaining} minutes")
        else:
            print(f"Failed to place order: {result}")
    
    def _view_customer_orders(self):
        print("\n===== My Orders =====")
        orders = self.order_manager.get_customer_orders(self.current_user.id)
        
        if not orders:
            print("You have no orders.")
            input("\nPress Enter to continue...")
            return
        
        orders.sort(key=lambda x: x.created_at, reverse=True)
        
        for order in orders:
            print(f"\nOrder ID: {order.id}")
            print(f"Date: {datetime.fromisoformat(order.created_at).strftime('%Y-%m-%d %H:%M')}")
            print(f"Status: {order.status.value}")
            print(f"Type: {order.order_type.value}")
            
            if order.order_type == OrderType.DELIVERY and order.delivery_address:
                print(f"Delivery Address: {order.delivery_address}")
            
            print("Items:")
            for item in order.items:
                print(f"  {item['quantity']}x {item['name']} - ${float(item['price']) * item['quantity']:.2f}")
            
            print(f"Total: ${order.total_amount:.2f}")
            
            # Show time remaining if applicable
            if order.status not in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP, OrderStatus.CANCELLED]:
                time_remaining = self.order_manager.get_time_remaining(order.id)
                if time_remaining:
                    if order.order_type == OrderType.DELIVERY:
                        print(f"Estimated time until delivery: {time_remaining} minutes")
                    else:
                        print(f"Estimated time until pickup: {time_remaining} minutes")
        
        input("\nPress Enter to continue...")
    
    def _track_order(self):
        order_id = input("\nEnter Order ID to track: ")
        order = self.order_manager.get_order(order_id)
        
        if not order:
            print("Order not found.")
            input("\nPress Enter to continue...")
            return
        
        if order.customer_id != self.current_user.id:
            print("This is not your order.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nOrder ID: {order.id}")
        print(f"Status: {order.status.value}")
        
        if order.status not in [OrderStatus.DELIVERED, OrderStatus.PICKED_UP, OrderStatus.CANCELLED]:
            time_remaining = self.order_manager.get_time_remaining(order.id)
            if time_remaining:
                if order.order_type == OrderType.DELIVERY:
                    print(f"Estimated time until delivery: {time_remaining} minutes")
                else:
                    print(f"Estimated time until pickup: {time_remaining} minutes")
        
        input("\nPress Enter to continue...")
    
    def _view_all_orders(self):
        print("\n===== All Orders =====")
        orders = self.order_manager.get_all_orders()
        
        if not orders:
            print("No orders found.")
            input("\nPress Enter to continue...")
            return
        
        orders.sort(key=lambda x: x.created_at, reverse=True)
        
        for order in orders:
            print(f"\nOrder ID: {order.id}")
            print(f"Date: {datetime.fromisoformat(order.created_at).strftime('%Y-%m-%d %H:%M')}")
            print(f"Status: {order.status.value}")
            print(f"Type: {order.order_type.value}")
            print(f"Total: ${order.total_amount:.2f}")
        
        input("\nPress Enter to continue...")
    
    def _update_order_status(self):
        order_id = input("\nEnter Order ID to update: ")
        order = self.order_manager.get_order(order_id)
        
        if not order:
            print("Order not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nCurrent Status: {order.status.value}")
        print("\nSelect new status:")
        print("1. Confirmed")
        print("2. Preparing")
        print("3. Ready")
        print("4. Out for Delivery (for delivery orders)")
        print("5. Delivered (for delivery orders)")
        print("6. Picked Up (for takeaway orders)")
        print("7. Cancelled")
        
        choice = input("Enter your choice: ")
        
        new_status = None
        if choice == "1":
            new_status = OrderStatus.CONFIRMED
        elif choice == "2":
            new_status = OrderStatus.PREPARING
        elif choice == "3":
            new_status = OrderStatus.READY
        elif choice == "4" and order.order_type == OrderType.DELIVERY:
            new_status = OrderStatus.OUT_FOR_DELIVERY
        elif choice == "5" and order.order_type == OrderType.DELIVERY:
            new_status = OrderStatus.DELIVERED
        elif choice == "6" and order.order_type == OrderType.TAKEAWAY:
            new_status = OrderStatus.PICKED_UP
        elif choice == "7":
            new_status = OrderStatus.CANCELLED
        else:
              print("Invalid choice or status not applicable to this order type.")
              input("\nPress Enter to continue...")
              return
        
        success, message = self.order_manager.update_order_status(order_id, new_status)
        print(message)
        input("\nPress Enter to continue...")
    
    def _manage_menu(self):
        while True:
            print("\n===== Manage Menu =====")
            print("1. View Menu")
            print("2. Add Menu Item")
            print("3. Update Menu Item")
            print("4. Remove Menu Item")
            print("5. Back to Main Menu")
            
            choice = input("Enter your choice: ")
            
            if choice == "1":
                self._display_menu()
            elif choice == "2":
                self._add_menu_item()
            elif choice == "3":
                self._update_menu_item()
            elif choice == "4":
                self._remove_menu_item()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _add_menu_item(self):
        print("\n===== Add Menu Item =====")
        name = input("Enter item name: ")
        description = input("Enter description: ")
        
        try:
            price = float(input("Enter price: $"))
            if price <= 0:
                print("Price must be positive.")
                return
        except ValueError:
            print("Invalid price. Please enter a number.")
            return
        
        category = input("Enter category: ")
        
        item = self.menu_manager.add_item(name, description, price, category)
        print(f"Item added successfully with ID: {item.id}")
    
    def _update_menu_item(self):
        item_id = input("\nEnter Item ID to update: ")
        item = self.menu_manager.get_item(item_id)
        
        if not item:
            print("Item not found.")
            return
        
        print(f"\nCurrent details for '{item.name}':")
        print(f"Description: {item.description}")
        print(f"Price: ${item.price:.2f}")
        print(f"Category: {item.category}")
        
        print("\nLeave field empty to keep current value.")
        name = input("New name (or enter to keep current): ")
        description = input("New description (or enter to keep current): ")
        price_str = input("New price (or enter to keep current): $")
        category = input("New category (or enter to keep current): ")
        
        updates = {}
        if name:
            updates["name"] = name
        if description:
            updates["description"] = description
        if price_str:
            try:
                price = float(price_str)
                if price <= 0:
                    print("Price must be positive.")
                    return
                updates["price"] = price
            except ValueError:
                print("Invalid price. Update cancelled.")
                return
        if category:
            updates["category"] = category
        
        if not updates:
            print("No changes made.")
            return
        
        success, message = self.menu_manager.update_item(item_id, **updates)
        print(message)
    
    def _remove_menu_item(self):
        item_id = input("\nEnter Item ID to remove: ")
        item = self.menu_manager.get_item(item_id)
        
        if not item:
            print("Item not found.")
            return
        
        confirm = input(f"Are you sure you want to remove '{item.name}'? (y/n): ")
        if confirm.lower() != 'y':
            print("Removal cancelled.")
            return
        
        success, message = self.menu_manager.remove_item(item_id)
        print(message)
    
    def _view_agent_orders(self):
        print("\n===== My Assigned Orders =====")
        orders = self.delivery_manager.get_agent_orders(self.current_user.id)
        
        if not orders:
            print("You have no assigned orders.")
            input("\nPress Enter to continue...")
            return
        
        orders.sort(key=lambda x: x.created_at, reverse=True)
        
        for order in orders:
         print(f"Order ID: {order.id}")
         try:
            # Use strptime instead of fromisoformat
            order_date = datetime.strptime(order.created_at, "%Y-%m-%dT%H:%M:%S.%f")
            print(f"Date: {order_date.strftime('%Y-%m-%d %H:%M')}")
         except ValueError:
            # Fallback if the datetime string doesn't have milliseconds
            order_date = datetime.strptime(order.created_at, "%Y-%m-%dT%H:%M:%S")
            print(f"Date: {order_date.strftime('%Y-%m-%d %H:%M')}")
        
        print(f"Status: {order.status.value}")
        print(f"Type: {order.order_type.value}")
        print(f"Total: ${order.total_amount:.2f}\n")
    
    input("Press Enter to continue...")
    
    def _update_delivery_status(self):
        orders = self.delivery_manager.get_agent_orders(self.current_user.id)
        active_orders = [order for order in orders if order.status != OrderStatus.DELIVERED]
        
        if not active_orders:
            print("\nYou have no active orders to update.")
            input("\nPress Enter to continue...")
            return
        
        print("\n===== Update Delivery Status =====")
        for i, order in enumerate(active_orders, 1):
            print(f"{i}. Order ID: {order.id} - Status: {order.status.value}")
        
        try:
            idx = int(input("\nEnter number to select order: ")) - 1
            if idx < 0 or idx >= len(active_orders):
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        
        selected_order = active_orders[idx]
        print(f"\nSelected Order ID: {selected_order.id}")
        print(f"Current Status: {selected_order.status.value}")
        
        print("\nSelect new status:")
        if selected_order.status == OrderStatus.CONFIRMED:
            print("1. Out for Delivery")
        elif selected_order.status == OrderStatus.READY:
            print("1. Out for Delivery")
        elif selected_order.status == OrderStatus.OUT_FOR_DELIVERY:
            print("1. Delivered")
        else:
            print("No valid status updates available for this order.")
            input("\nPress Enter to continue...")
            return
        
        choice = input("Enter your choice: ")
        
        new_status = None
        if choice == "1":
            if selected_order.status in [OrderStatus.CONFIRMED, OrderStatus.READY]:
                new_status = OrderStatus.OUT_FOR_DELIVERY
            elif selected_order.status == OrderStatus.OUT_FOR_DELIVERY:
                new_status = OrderStatus.DELIVERED
        
        if not new_status:
            print("Invalid choice.")
            input("\nPress Enter to continue...")
            return
        
        success, message = self.order_manager.update_order_status(
            selected_order.id, 
            new_status, 
            self.current_user.id
        )
        print(message)
        input("\nPress Enter to continue...")
    
    def _view_all_agents(self):
        print("\n===== All Delivery Agents =====")
        data_store = DataStore()
        agents = data_store.get_delivery_agents()
        
        if not agents:
            print("No delivery agents found.")
            input("\nPress Enter to continue...")
            return
        
        for agent_id, agent_data in agents.items():
            print(f"\nAgent ID: {agent_id}")
            print(f"Name: {agent_data['name']}")
            print(f"Status: {agent_data['status']}")
            if agent_data['current_order']:
                print(f"Current Order: {agent_data['current_order']}")
        
        input("\nPress Enter to continue...")
    
    def _register_staff(self):
        print("\n===== Register New Staff =====")
        print("1. Register Restaurant Manager")
        print("2. Register Delivery Agent")
        print("3. Register Admin")
        print("4. Back")
        
        choice = input("Enter your choice: ")
        
        if choice == "4":
            return
        
        username = input("Enter username: ")
        password = input("Enter password: ")
        name = input("Enter full name: ")
        
        role = None
        if choice == "1":
            role = UserRole.RESTAURANT_MANAGER
        elif choice == "2":
            role = UserRole.DELIVERY_AGENT
        elif choice == "3":
            role = UserRole.ADMIN
        else:
            print("Invalid choice.")
            return
        
        success, message = self.user_manager.register_user(username, password, role, name)
        print(message)

# Main entry point
if __name__ == "__main__":
    app = FoodDeliveryApp()
    app.start()
          