from customer import Customer
from typing import Dict
import uuid
from product import Product
from delivery import Delivery
from order import Order

class RetailStore(Customer):
    def __init__(self, name: str, email: str, password: str, store_name: str):
        super().__init__(name, email, password)
        self.store_name = store_name
        self.business_id = str(uuid.uuid4())
    
    def apply_bulk_discount(self) -> float:
        """Get bulk discount for retail stores"""
        return 0.15  # 15% bulk discount
    
    def manage_products(self, e_store: 'EStore') -> None:
        """Manage products in the e-store"""
        if not self.is_logged_in:
            print("Please log in to manage products.")
            return

        while True:
            print("\n==== Product Management ====")
            print("1. View all products")
            print("2. Add a new product")
            print("3. Update a product")
            print("4. Delete a product")
            print("5. Back to main menu")

            choice = input("Enter your choice (1-5): ")

            if choice == "1":
                self._view_all_products(e_store)
            elif choice == "2":
                self._add_product(e_store)
            elif choice == "3":
                self._update_product(e_store)
            elif choice == "4":
                self._delete_product(e_store)
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")

    def _view_all_products(self, e_store: 'EStore') -> None:
        """View all products"""
        products = e_store.products
        if not products:
            print("No products available.")
            return

        print("\n==== All Products ====")
        for product in products:
            print(f"ID: {product.product_id}")
            print(f"Name: {product.name}")
            print(f"Category: {product.category}")
            print(f"Price: ${product.price:.2f}")
            print(f"Stock: {product.stock}")
            print("------------------------")

    def _add_product(self, e_store: 'EStore') -> None:
        """Add a new product"""
        name = input("Enter product name: ")
        category = input("Enter product category: ")

        try:
            price = float(input("Enter product price: $"))
            stock = int(input("Enter product stock quantity: "))
        except ValueError:
            print("Invalid input. Price and stock must be numbers.")
            return

        product = Product(name, category, price, stock)
        e_store.add_product(product)
        print(f"Product '{name}' added successfully!")

    def _update_product(self, e_store: 'EStore') -> None:
        """Update an existing product"""
        product_id = input("Enter product ID to update: ")
        product = e_store.get_product(product_id)

        if not product:
            print(f"Product with ID {product_id} not found.")
            return

        print(f"Updating product: {product.name}")

        name = input(f"Enter new name (current: {product.name}), or press Enter to keep current: ")
        if name:
            product.name = name

        category = input(f"Enter new category (current: {product.category}), or press Enter to keep current: ")
        if category:
            product.category = category

        price_str = input(f"Enter new price (current: ${product.price:.2f}), or press Enter to keep current: $")
        if price_str:
            try:
                product.price = float(price_str)
            except ValueError:
                print("Invalid price. Price must be a number.")

        stock_str = input(f"Enter new stock quantity (current: {product.stock}), or press Enter to keep current: ")
        if stock_str:
            try:
                new_stock = int(stock_str)
                # Update stock relative to current value
                product.update_stock(new_stock - product.stock)
            except ValueError:
                print("Invalid stock quantity. Stock must be a number.")

        print(f"Product '{product.name}' updated successfully!")

    def _delete_product(self, e_store: 'EStore') -> None:
        """Delete a product"""
        product_id = input("Enter product ID to delete: ")

        if e_store.delete_product(product_id):
            print(f"Product with ID {product_id} deleted successfully!")
        else:
            print(f"Product with ID {product_id} not found.")

    def view_orders(self, e_store: 'EStore') -> None:
        """View all orders"""
        if not self.is_logged_in:
            print("Please log in to view orders.")
            return

        orders = e_store.orders
        if not orders:
            print("No orders available.")
            return

        print("\n==== All Orders ====")
        for order in orders:
            print(f"Order ID: {order.order_id}")
            print(f"Customer: {order.customer.name}")
            print(f"Date: {order.date}")
            print(f"Status: {order.status}")
            print(f"Total: ${order.total_price:.2f}")
            print("Items:")
            for item in order.items:
                product = e_store.get_product(item["product_id"])
                if product:
                    print(f"  - {item['quantity']}x {product.name} (${product.price:.2f} each)")
            print("------------------------")

    def manage_delivery(self, e_store: 'EStore') -> None:
        """Manage deliveries for orders"""
        if not self.is_logged_in:
            print("Please log in to manage deliveries.")
            return

        orders = [order for order in e_store.orders if order.status != "Delivered"]
        if not orders:
            print("No pending deliveries.")
            return

        print("\n==== Pending Deliveries ====")
        for i, order in enumerate(orders, 1):
            print(f"{i}. Order ID: {order.order_id} - Status: {order.status}")

        try:
            idx = int(input("Enter the number of the order to update (0 to cancel): ")) - 1
            if idx == -1:
                return
            if idx < 0 or idx >= len(orders):
                print("Invalid selection.")
                return

            order = orders[idx]

            # Check if delivery exists
            delivery = None
            for d in e_store.deliveries:
                if d.order_id == order.order_id:
                    delivery = d
                    break

            if not delivery:
                # Create new delivery if it doesn't exist
                delivery_date = datetime.datetime.now() + datetime.timedelta(days=3)
                delivery = Delivery(order.order_id, delivery_date.strftime("%Y-%m-%d"))
                e_store.deliveries.append(delivery)

            print(f"\nUpdating delivery for Order ID: {order.order_id}")
            print(f"Current status: {delivery.status}")
            print("\nAvailable statuses:")
            print("1. Processing")
            print("2. Shipped")
            print("3. Out for Delivery")
            print("4. Delivered")

            status_choice = input("Enter new status (1-4): ")
            status_map = {
                "1": "Processing",
                "2": "Shipped",
                "3": "Out for Delivery",
                "4": "Delivered"
            }

            if status_choice in status_map:
                new_status = status_map[status_choice]
                delivery.update_status(new_status)

                # Update order status too
                if new_status == "Delivered":
                    order.status = "Delivered"
                else:
                    order.status = "In Transit"

                print(f"Delivery status updated to: {new_status}")
            else:
                print("Invalid status choice.")

        except ValueError:
            print("Invalid input. Please enter a number.")
    
    def to_dict(self) -> Dict:
        """Convert retail store object to dictionary for storage"""
        data = super().to_dict()
        data["store_name"] = self.store_name
        data["business_id"] = self.business_id
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RetailStore':
        """Create retail store object from dictionary"""
        # Create the RetailStore with all required parameters
        store = cls(
            name=data["name"], 
            email=data["email"], 
            password="", 
            store_name=data["store_name"]
        )
        # Set additional properties
        store.user_id = data["user_id"]
        store.password = data["password"]  # Already hashed
        store.business_id = data["business_id"]
        store.order_history = data.get("order_history", [])
        return store