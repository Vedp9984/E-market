import os
import json
import uuid
import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Union, Optional
from user import User
from customer import Customer
from retail_store import RetailStore
from order import Order
from discount import Discount
from payment import Payment
from admin import Admin
from delivery import Delivery
from estore import EStore


class DollMartCLI:
    def __init__(self):
        self.e_store = EStore.get_instance()
        self.current_user = None

    def start(self) -> None:
        """Start the CLI interface"""
        print("=" * 50)
        print("Welcome to DollMart CLI")
        print("=" * 50)

        while True:
            self._display_main_menu()
            choice = input("Enter your choice: ")

            if choice == "1":
                self._register_user()
            elif choice == "2":
                self._login()
            elif choice == "3":
                self._search_products()
            elif choice == "4":
                if self._check_login():
                    if isinstance(self.current_user, Customer):
                        self._place_order()
                    else:
                        print("Only customers can place orders.")
            elif choice == "5":
                if self._check_login():
                    if isinstance(self.current_user, Customer):
                        self.current_user.view_order_history(self.e_store)
                    else:
                        print("Only customers can view order history.")
            elif choice == "6":
                if self._check_login():
                    if isinstance(self.current_user, RetailStore):
                        self.current_user.manage_products(self.e_store)
                    else:
                        print("Only retail store owners can manage products.")
            elif choice == "7":
                if self._check_login():
                    if isinstance(self.current_user, RetailStore):
                        self.current_user.view_orders(self.e_store)
                    else:
                        print("Only retail store owners can view orders.")
            elif choice == "8":
                if self._check_login():
                    if isinstance(self.current_user, RetailStore):
                        self.current_user.manage_delivery(self.e_store)
                    else:
                        print("Only retail store owners can manage deliveries.")
            elif choice == "9":
                if self.current_user:
                    self.current_user.logout()
                    self.current_user = None
                    print("Logged out successfully.")
                else:
                    print("You are not logged in.")
            elif choice == "10":
                if self._check_login():
                    if isinstance(self.current_user, Admin):
                        self.current_user.view_retail_stores(self.e_store)
                    else:
                        print("Only admins can view retail stores.")
            elif choice == "0":
                print("Thank you for using DollMart CLI. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def _display_main_menu(self) -> None:
        """Display the main menu options"""
        print("\n==== Main Menu ====")
        print("1. Register")
        print("2. Login")
        print("3. Search Products")

        if self.current_user:
            print("4. Place Order")
            print("5. View Order History")

            if isinstance(self.current_user, RetailStore):
                print("6. Manage Products")
                print("7. View Orders")
                print("8. Manage Deliveries")
            elif isinstance(self.current_user, Admin):
                print("10. View Retail Stores")

            print("9. Logout")

        print("0. Exit")

    def _register_user(self) -> None:
        """Register a new user"""
        print("\n==== Register ====")
        print("1. Register as Customer")
        print("2. Register as Retail Store")
        print("3. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice not in ["1", "2"]:
            return

        name = input("Enter your name: ")
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        # Check if email already exists
        if self.e_store.get_user(email):
            print("User with this email already exists. Please login instead.")
            return

        if choice == "1":
            user = Customer(name, email, password)
            print("Customer account created successfully!")
        else:
            store_name = input("Enter your store name: ")
            user = RetailStore(name, email, password, store_name)
            print("Retail store account created successfully!")

        self.e_store.add_user(user)

    def _login(self) -> None:
        """Login a user"""
        if self.current_user:
            print("You are already logged in.")
            return

        print("\n==== Login ====")
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        user = self.e_store.get_user(email)
        if not user:
            print("User not found.")
            return

        if user.login(password):
            self.current_user = user
        else:
            print("Login failed. Please check your credentials.")

    def _check_login(self) -> bool:
        """Check if user is logged in"""
        if not self.current_user:
            print("Please login first.")
            return False
        return True

    def _search_products(self) -> None:
        """Search for products"""
        print("\n==== Search Products ====")
        query = input("Enter search query (or leave blank to see all products): ")

        if query:
            products = self.e_store.search_product(query)
        else:
            products = self.e_store.products

        if not products:
            print("No products found.")
            return

        print("\n==== Search Results ====")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name}")
            print(f"   Category: {product.category}")
            print(f"   Price: ${product.price:.2f}")
            print(f"   In Stock: {product.stock}")
            print("   -------------------")

        # View details for a specific product
        choice = input("Enter product number for details (or 0 to go back): ")
        try:
            choice = int(choice)
            if choice > 0 and choice <= len(products):
                product = products[choice - 1]
                print(f"\nProduct ID: {product.product_id}")
                print(f"Name: {product.name}")
                print(f"Category: {product.category}")
                print(f"Price: ${product.price:.2f}")
                print(f"Stock: {product.stock}")
        except ValueError:
            pass

    def _place_order(self) -> None:
        """Place a new order"""
        if not isinstance(self.current_user, Customer):
            print("Only customers can place orders.")
            return

        # Display available products
        print("\n==== Available Products ====")
        products = self.e_store.products
        if not products:
            print("No products available.")
            return

        for i, product in enumerate(products, 1):
            print(f"{i}. {product.name} - ${product.price:.2f} ({product.stock} in stock)")

        # Build cart
        cart = []
        while True:
            try:
                product_idx = int(input("\nEnter product number to add to cart (0 to finish): "))
                if product_idx == 0:
                    break
                if product_idx < 1 or product_idx > len(products):
                    print("Invalid product number.")
                    continue

                product = products[product_idx - 1]
                if product.stock == 0:
                    print(f"Sorry, {product.name} is out of stock.")
                    continue

                quantity = int(input(f"Enter quantity for {product.name} (max {product.stock}): "))
                if quantity <= 0:
                    print("Quantity must be positive.")
                    continue
                if quantity > product.stock:
                    print(f"Only {product.stock} available.")
                    continue

                cart.append({
                    "product_id": product.product_id,
                    "quantity": quantity
                })

                print(f"{quantity}x {product.name} added to cart.")

                if input("Add more products? (y/n): ").lower() != 'y':
                    break
            except ValueError:
                print("Please enter a valid number.")

        if not cart:
            print("Cart is empty. Order cancelled.")
            return

        # Show order summary
        total = 0
        print("\n==== Order Summary ====")
        for item in cart:
            product = self.e_store.get_product(item["product_id"])
            item_total = product.price * item["quantity"]
            total += item_total
            print(f"{item['quantity']}x {product.name} - ${item_total:.2f}")

        print(f"\nSubtotal: ${total:.2f}")

        # Apply customer discount if any
        if isinstance(self.current_user, RetailStore):
            discount_percent = self.current_user.apply_bulk_discount() * 100
            discount_amount = total * self.current_user.apply_bulk_discount()
            total -= discount_amount
            print(f"Retail Store Discount ({discount_percent:.1f}%): -${discount_amount:.2f}")
        elif isinstance(self.current_user, Customer):
            discount_percent = self.current_user.get_discount() * 100
            discount_amount = total * self.current_user.get_discount()
            total -= discount_amount
            print(f"Customer Discount ({discount_percent:.1f}%): -${discount_amount:.2f}")

        print(f"Total: ${total:.2f}")

        # Confirm order
        if input("\nConfirm order? (y/n): ").lower() != 'y':
            print("Order cancelled.")
            return

        # Select payment method
        print("\n==== Payment Method ====")
        print("1. Credit Card")
        print("2. PayPal")
        print("3. Bank Transfer")

        payment_choice = input("Select payment method: ")
        payment_methods = {
            "1": "Credit Card",
            "2": "PayPal",
            "3": "Bank Transfer"
        }

        if payment_choice not in payment_methods:
            print("Invalid payment method. Order cancelled.")
            return

        payment_method = payment_methods[payment_choice]

        # Place order
        order = self.current_user.place_order(self.e_store, cart, payment_method)
        if order:
            print(f"\nOrder placed successfully!")
            print(f"Order ID: {order.order_id}")
            print(f"Total: ${order.total_price:.2f}")
            print(f"Status: {order.status}")
            if order.delivery:
                print(f"Expected delivery date: {order.delivery.expected_date}")

# --- Run the Application ---

if __name__ == "__main__":
    cli = DollMartCLI()
    cli.start()