import pytest
import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
sys.path.insert(0, src_dir)

from user import User
from customer import Customer
from retail_store import RetailStore
from admin import Admin
from product import Product
from order import Order
from delivery import Delivery
from order import Order
from payment import Payment
from discount import Discount
from estore import EStore




# Fixture to create a clean EStore instance for each test
@pytest.fixture
def clean_estore():
    # Reset the singleton instance
    EStore._instance = None
    
    # Delete any existing data files
    if os.path.exists("data"):
        for filename in os.listdir("data"):
            os.remove(os.path.join("data", filename))
    
    # Create a new instance
    estore = EStore.get_instance()
    return estore


# Fixture to create test users
@pytest.fixture
def test_users(clean_estore):
    estore = clean_estore
    
    # Create test customer
    customer = Customer("Test Customer", "customer@test.com", "password123")
    estore.add_user(customer)
    
    # Create test retail store
    retail_store = RetailStore("Test Store Owner", "store@test.com", "password123", "Test Store")
    estore.add_user(retail_store)
    
    # Admin is already created in EStore initialization
    admin = None
    for user in estore.users:
        if isinstance(user, Admin):
            admin = user
            break
    
    return {"customer": customer, "retail_store": retail_store, "admin": admin}


# Fixture to create test products
@pytest.fixture
def test_products(clean_estore):
    estore = clean_estore
    
    # Create test products
    product1 = Product("Test Product 1", "Electronics", 199.99, 10)
    product2 = Product("Test Product 2", "Clothing", 49.99, 20)
    product3 = Product("Test Product 3", "Home", 99.99, 0)  # Out of stock
    
    estore.add_product(product1)
    estore.add_product(product2)
    estore.add_product(product3)
    
    return [product1, product2, product3]


# Fixture to create test orders
@pytest.fixture
def test_orders(clean_estore, test_users, test_products):
    estore = clean_estore
    customer = test_users["customer"]
    products = test_products
    
    # Log in customer
    customer.login("password123")
    
    # Create order items
    items = [
        {"product_id": products[0].product_id, "quantity": 1},
        {"product_id": products[1].product_id, "quantity": 2}
    ]
    
    # Place an order
    order = customer.place_order(estore, items, "Credit Card")
    
    return [order]


# Test User class
class TestUser:
    def test_user_creation(self):
        """Test user creation with correct attributes"""
        user = User("Test User", "test@example.com", "password123")
        
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.is_logged_in == False
        assert user.password != "password123"  # Password should be hashed
    
    def test_user_login_valid(self):
        """Test user login with valid credentials"""
        user = User("Test User", "test@example.com", "password123")
        result = user.login("password123")
        
        assert result == True
        assert user.is_logged_in == True
    
    def test_user_login_invalid(self):
        """Test user login with invalid credentials"""
        user = User("Test User", "test@example.com", "password123")
        result = user.login("wrongpassword")
        
        assert result == False
        assert user.is_logged_in == False
    
    def test_user_logout(self):
        """Test user logout"""
        user = User("Test User", "test@example.com", "password123")
        user.login("password123")
        user.logout()
        
        assert user.is_logged_in == False
    
    def test_user_to_dict(self):
        """Test user serialization to dictionary"""
        user = User("Test User", "test@example.com", "password123")
        user_dict = user.to_dict()
        
        assert user_dict["name"] == "Test User"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["type"] == "User"
        assert "user_id" in user_dict
        assert "password" in user_dict
    
    def test_user_from_dict(self):
        """Test user deserialization from dictionary"""
        original_user = User("Test User", "test@example.com", "password123")
        user_dict = original_user.to_dict()
        
        new_user = User.from_dict(user_dict)
        
        assert new_user.name == original_user.name
        assert new_user.email == original_user.email
        assert new_user.password == original_user.password
        assert new_user.user_id == original_user.user_id


# Test Customer class
class TestCustomer:
    def setUp(self):
        # Mock all the necessary components
        self.mock_data_store = MagicMock()
        self.patcher1 = patch('classes.DataStore', return_value=self.mock_data_store)
        self.mock_data_store_class = self.patcher1.start()
        
        # Set up menu items data
        self.menu_items = {
            "item1": {
                "id": "item1", 
                "name": "Pizza", 
                "description": "Delicious pizza", 
                "price": 10.99, 
                "category": "Main"
            },
            "item2": {
                "id": "item2", 
                "name": "Burger", 
                "description": "Tasty burger", 
                "price": 8.99, 
                "category": "Main"
            }
        }
        self.mock_data_store.get_menu_items.return_value = self.menu_items
        
        # Set up orders data
        self.orders = {}
        self.mock_data_store.get_orders.return_value = self.orders
        
        # Create manager instances
        self.user_manager = UserManager()
        self.menu_manager = MenuManager()
        self.order_manager = OrderManager()
        
        self.user_manager.register_user("testcustomer", "password123", UserRole.CUSTOMER, "Test Customer")
        success, self.customer = self.user_manager.authenticate("testcustomer", "password123")
    def tearDown(self):
        self.patcher1.stop()
    def test_customer_creation(self):
        """Test customer creation with correct attributes"""
        customer = Customer("Test Customer", "customer@test.com", "password123")
        
        assert customer.name == "Test Customer"
        assert customer.email == "customer@test.com"
        assert customer.is_logged_in == False
        assert customer.order_history == []
    
    def test_customer_get_discount(self):
        """Test customer discount calculation"""
        customer = Customer("Test Customer", "customer@test.com", "password123")
        
        assert customer.get_discount() == 0.05  # Should be 5%
    def test_customer_place_order(self, clean_estore, test_users, test_products):
        """Test customer placing an order"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        # Log in customer
        customer.login("password123")
        
        # Define order items
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        
        # Place the order
        order = customer.place_order(estore, items, "Credit Card")
        
        # Check order was created correctly
        assert order.customer == customer
        assert order.items == items
        assert order.payment_method == "Credit Card"
        assert order.status == "Confirmed"
        assert order.total_price == products[0].price
        assert hasattr(order, "order_id")
        assert hasattr(order, "date")
    
    
    def test_customer_place_order_not_logged_in(self, clean_estore, test_products):
        """Test customer placing an order while not logged in"""
        estore = clean_estore
        products = test_products
        
        customer = Customer("Test Customer", "customer@test.com", "password123")
        estore.add_user(customer)
        # Not logged in
        
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = customer.place_order(estore, items, "Credit Card")
        
        assert order is None
        assert products[0].stock == 10  # Stock unchanged
    
    def test_customer_place_order_insufficient_stock(self, clean_estore, test_products):
        """Test customer placing an order with insufficient stock"""
        estore = clean_estore
        products = test_products
        
        customer = Customer("Test Customer", "customer@test.com", "password123")
        estore.add_user(customer)
        customer.login("password123")
        
        # Try to order more than available stock
        items = [{"product_id": products[0].product_id, "quantity": 20}]
        order = customer.place_order(estore, items, "Credit Card")
        
        assert order is None
        assert products[0].stock == 10  # Stock unchanged
    
    def test_customer_place_order_out_of_stock(self, clean_estore, test_products):
        """Test customer placing an order for an out-of-stock product"""
        estore = clean_estore
        products = test_products
        
        customer = Customer("Test Customer", "customer@test.com", "password123")
        estore.add_user(customer)
        customer.login("password123")
        
        # Product 3 is out of stock
        items = [{"product_id": products[2].product_id, "quantity": 1}]
        order = customer.place_order(estore, items, "Credit Card")
        
        assert order is None
    
    def test_customer_place_order_invalid_product(self, clean_estore):
        """Test customer placing an order with invalid product ID"""
        estore = clean_estore
        
        customer = Customer("Test Customer", "customer@test.com", "password123")
        estore.add_user(customer)
        customer.login("password123")
        
        # Invalid product ID
        items = [{"product_id": "invalid-id", "quantity": 1}]
        order = customer.place_order(estore, items, "Credit Card")
        
        assert order is None
    
    def test_customer_view_order_history_empty(self, clean_estore):
        """Test viewing empty order history"""
        estore = clean_estore
        
        customer = Customer("Test Customer", "customer@test.com", "password123")
        estore.add_user(customer)
        customer.login("password123")
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            customer.view_order_history(estore)
            mock_print.assert_any_call("You haven't placed any orders yet.")
    
    def test_customer_view_order_history(self, clean_estore, test_products):
        """Test viewing order history with orders"""
        estore = clean_estore
        products = test_products
        
        customer = Customer("Test Customer", "customer@test.com", "password123")
        estore.add_user(customer)
        customer.login("password123")
        
        # Place an order
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = customer.place_order(estore, items, "Credit Card")
        order_id = order.order_id 
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            customer.view_order_history(estore)
            mock_print.assert_any_call(f"Order ID: {order_id}")
    
    def test_customer_to_dict(self):
        """Test customer serialization to dictionary"""
        customer = Customer("Test Customer", "customer@test.com", "password123")
        customer_dict = customer.to_dict()
        
        assert customer_dict["name"] == "Test Customer"
        assert customer_dict["email"] == "customer@test.com"
        assert customer_dict["type"] == "Customer"
        assert "order_history" in customer_dict
    
    def test_customer_from_dict(self):
        """Test customer deserialization from dictionary"""
        original_customer = Customer("Test Customer", "customer@test.com", "password123")
        original_customer.order_history = ["order1", "order2"]
        customer_dict = original_customer.to_dict()
        
        new_customer = Customer.from_dict(customer_dict)
        
        assert new_customer.name == original_customer.name
        assert new_customer.email == original_customer.email
        assert new_customer.password == original_customer.password
        assert new_customer.order_history == original_customer.order_history


# Test RetailStore class
class TestRetailStore:
    def test_retail_store_creation(self):
        """Test retail store creation with correct attributes"""
        store = RetailStore("Store Owner", "store@test.com", "password123", "Test Store")
        
        assert store.name == "Store Owner"
        assert store.email == "store@test.com"
        assert store.store_name == "Test Store"
        assert store.is_logged_in == False
        assert hasattr(store, "business_id")
    
    def test_retail_store_apply_bulk_discount(self):
        """Test retail store bulk discount calculation"""
        store = RetailStore("Store Owner", "store@test.com", "password123", "Test Store")
        
        assert store.apply_bulk_discount() == 0.15  # Should be 15%
    
    def test_retail_store_add_product(self, clean_estore):
        """Test retail store adding a product"""
        estore = clean_estore
        
        store = RetailStore("Store Owner", "store@test.com", "password123", "Test Store")
        estore.add_user(store)
        store.login("password123")
        
        # Mock user input for product creation
        with patch('builtins.input', side_effect=["Test Product", "Electronics", "199.99", "10"]):
            with patch('builtins.print') as mock_print:
                store._add_product(estore)
        
        # Product should be added to estore
        assert len(estore.products) == 1
        assert estore.products[0].name == "Test Product"
        assert estore.products[0].category == "Electronics"
        assert estore.products[0].price == 199.99
        assert estore.products[0].stock == 10
    
    def test_retail_store_update_product(self, clean_estore):
        """Test retail store updating a product"""
        estore = clean_estore
        
        store = RetailStore("Store Owner", "store@test.com", "password123", "Test Store")
        estore.add_user(store)
        store.login("password123")
        
        # Add a product first
        product = Product("Test Product", "Electronics", 199.99, 10)
        estore.add_product(product)
        
        # Mock user input for product update
        with patch('builtins.input', side_effect=[
            product.product_id,  # Product ID
            "Updated Product",   # New name
            "Gadgets",           # New category
            "299.99",            # New price
            "15"                 # New stock
        ]):
            with patch('builtins.print'):
                store._update_product(estore)
        
        # Product should be updated
        updated_product = estore.get_product(product.product_id)
        assert updated_product.name == "Updated Product"
        assert updated_product.category == "Gadgets"
        assert updated_product.price == 299.99
        assert updated_product.stock == 15
    
    def test_retail_store_delete_product(self, clean_estore):
        """Test retail store deleting a product"""
        estore = clean_estore
        
        store = RetailStore("Store Owner", "store@test.com", "password123", "Test Store")
        estore.add_user(store)
        store.login("password123")
        
        # Add a product first
        product = Product("Test Product", "Electronics", 199.99, 10)
        estore.add_product(product)
        
        # Mock user input for product deletion
        with patch('builtins.input', return_value=product.product_id):
            with patch('builtins.print'):
                store._delete_product(estore)
        
        # Product should be deleted
        assert len(estore.products) == 0
        assert estore.get_product(product.product_id) is None
    
    def test_retail_store_view_orders(self, clean_estore, test_users, test_products):
        """Test retail store viewing orders"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        store = test_users["retail_store"]
        store.login("password123")
        
        # Customer places an order
        customer.login("password123")
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = customer.place_order(estore, items, "Credit Card")
        
        # Retail store views orders
        with patch('builtins.print') as mock_print:
            store.view_orders(estore)
            mock_print.assert_any_call("\n==== All Orders ====")
            mock_print.assert_any_call(f"Order ID: {order.order_id}")
    
    def test_retail_store_manage_delivery(self, clean_estore, test_users, test_products):
        """Test retail store managing deliveries"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        store = test_users["retail_store"]
        store.login("password123")
        
        # Customer places an order
        customer.login("password123")
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = customer.place_order(estore, items, "Credit Card")
        
        # Mock user input for managing delivery
        with patch('builtins.input', side_effect=["1", "2"]):  # Select order 1, set status to "Shipped"
            with patch('builtins.print'):
                store.manage_delivery(estore)
        
        # Order status should be updated
        updated_order = estore.get_order(order.order_id)
        assert updated_order.status == "In Transit"
        assert updated_order.delivery.status == "Shipped"
    
    def test_retail_store_to_dict(self):
        """Test retail store serialization to dictionary"""
        store = RetailStore("Store Owner", "store@test.com", "password123", "Test Store")
        store_dict = store.to_dict()
        
        assert store_dict["name"] == "Store Owner"
        assert store_dict["email"] == "store@test.com"
        assert store_dict["store_name"] == "Test Store"
        assert "business_id" in store_dict
        assert "type" in store_dict
    
    def test_retail_store_from_dict(self):
        """Test retail store deserialization from dictionary"""
        original_store = RetailStore("Store Owner", "store@test.com", "password123", "Test Store")
        store_dict = original_store.to_dict()
        
        new_store = RetailStore.from_dict(store_dict)
        
        assert new_store.name == original_store.name
        assert new_store.email == original_store.email
        assert new_store.store_name == original_store.store_name
        assert new_store.business_id == original_store.business_id


# Test Admin class
class TestAdmin:
    def test_admin_creation(self):
        """Test admin creation with correct attributes"""
        admin = Admin("Admin User", "admin@test.com", "password123")
        
        assert admin.name == "Admin User"
        assert admin.email == "admin@test.com"
        assert admin.is_logged_in == False
    
    def test_admin_view_orders(self, clean_estore, test_users, test_products):
        """Test admin viewing all orders"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        admin = test_users["admin"]
        
        # Admin logs in
        admin.login("admin123")
        
        # Customer places an order
        customer.login("password123")
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        customer.place_order(estore, items, "Credit Card")
        
        # Admin views orders
        with patch('builtins.print') as mock_print:
            admin.view_orders(estore)
            mock_print.assert_any_call("==== All Orders ====")
    
    def test_admin_view_orders_not_logged_in(self, clean_estore):
        """Test admin viewing orders while not logged in"""
        estore = clean_estore
        admin = Admin("Admin User", "admin@test.com", "password123")
        
        # Admin not logged in
        with patch('builtins.print') as mock_print:
            admin.view_orders(estore)
            mock_print.assert_called_with("Please log in as admin to view orders.")
    
    def test_admin_view_retail_stores(self, clean_estore, test_users):
        """Test admin viewing retail stores"""
        estore = clean_estore
        admin = test_users["admin"]
        
        # Admin logs in
        admin.login("admin123")
        
        # Admin views retail stores
        
    
    def test_admin_view_retail_stores_not_logged_in(self, clean_estore):
        """Test admin viewing retail stores while not logged in"""
        estore = clean_estore
        admin = Admin("Admin User", "admin@test.com", "password123")
        
        # Admin not logged in
        with patch('builtins.print') as mock_print:
            admin.view_retail_stores(estore)
            mock_print.assert_called_with("Please log in as admin to view retail stores.")


# Test Product class
class TestProduct:
    def test_product_creation(self):
        """Test product creation with correct attributes"""
        product = Product("Test Product", "Electronics", 199.99, 10)
        
        assert product.name == "Test Product"
        assert product.category == "Electronics"
        assert product.price == 199.99
        assert product.stock == 10
        assert hasattr(product, "product_id")
    
    def test_product_update_stock_increase(self):
        """Test product stock increase"""
        product = Product("Test Product", "Electronics", 199.99, 10)
        product.update_stock(5)
        
        assert product.stock == 15
    
    def test_product_update_stock_decrease(self):
        """Test product stock decrease"""
        product = Product("Test Product", "Electronics", 199.99, 10)
        product.update_stock(-5)
        
        assert product.stock == 5
    
    def test_product_update_stock_below_zero(self):
        """Test product stock decrease below zero"""
        product = Product("Test Product", "Electronics", 199.99, 10)
        product.update_stock(-15)
        
        assert product.stock == 0  # Should not go below zero
    
    def test_product_apply_discount(self):
        """Test product discount calculation"""
        product = Product("Test Product", "Electronics", 100.00, 10)
        discounted_price = product.apply_discount(0.2)  # 20% discount
        
        assert discounted_price == 80.0
    
    def test_product_to_dict(self):
        """Test product serialization to dictionary"""
        product = Product("Test Product", "Electronics", 199.99, 10)
        product_dict = product.to_dict()
        
        assert product_dict["name"] == "Test Product"
        assert product_dict["category"] == "Electronics"
        assert product_dict["price"] == 199.99
        assert product_dict["stock"] == 10
        assert "product_id" in product_dict
    
    def test_product_from_dict(self):
        """Test product deserialization from dictionary"""
        original_product = Product("Test Product", "Electronics", 199.99, 10)
        product_dict = original_product.to_dict()
        
        new_product = Product.from_dict(product_dict)
        
        assert new_product.name == original_product.name
        assert new_product.category == original_product.category
        assert new_product.price == original_product.price
        assert new_product.stock == original_product.stock
        assert new_product.product_id == original_product.product_id


# Test Order class
class TestOrder:
    def test_order_creation(self, clean_estore, test_users, test_products):
        """Test order creation with correct attributes"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = Order(customer, items, "Credit Card")
        
        assert order.customer == customer
        assert order.items == items
        assert order.payment_method == "Credit Card"
        assert order.status == "Pending"
        assert order.total_price == products[0].price
        assert hasattr(order, "order_id")
        assert hasattr(order, "date")
    
    def test_order_calculate_total(self, clean_estore, test_users, test_products):
        """Test order total calculation"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        # Order with multiple items
        items = [
            {"product_id": products[0].product_id, "quantity": 1},
            {"product_id": products[1].product_id, "quantity": 2}
        ]
        order = Order(customer, items, "Credit Card")
        
        expected_total = products[0].price + (products[1].price * 2)
        assert order.total_price == expected_total
    
    def test_order_apply_discount_percentage(self, clean_estore, test_users, test_products):
        """Test applying percentage discount to order"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = Order(customer, items, "Credit Card")
        
        # Create a percentage discount (20%)
        discount = Discount("percentage", 0.2)
        original_price = order.total_price
        
        # Apply discount
        order.apply_discount(discount)
        
        assert order.total_price == original_price * 0.8
        assert order.discount_applied == discount
    
    def test_order_apply_discount_fixed(self, clean_estore, test_users, test_products):
        """Test applying fixed discount to order"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = Order(customer, items, "Credit Card")
        
        # Create a fixed discount ($50)
        discount = Discount("fixed", 50)
        original_price = order.total_price
        
        # Apply discount
        order.apply_discount(discount)
        
        assert order.total_price == original_price - 50
        assert order.discount_applied == discount
    
    def test_order_apply_discount_fixed_below_zero(self, clean_estore, test_users, test_products):
        """Test applying fixed discount greater than order total"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = Order(customer, items, "Credit Card")
        
        # Create a fixed discount larger than the order total
        discount = Discount("fixed", order.total_price + 100)
        
        # Apply discount
        order.apply_discount(discount)
        
        assert order.total_price == 0  # Price should not go below zero
        assert order.discount_applied == discount
    
    def test_order_track_order(self, clean_estore, test_users, test_products):
        """Test order tracking"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = Order(customer, items, "Credit Card")
        
        # Track order without delivery
        status = order.track_order()
        assert status == f"Order status: {order.status}"
        
        # Add delivery
        delivery = Delivery(order.order_id, "2023-12-31")
        order.delivery = delivery
        
        # Track order with delivery
        status = order.track_order()
        assert status == f"Order status: {order.status}, Delivery status: {delivery.status}"
    
    def test_order_to_dict(self, clean_estore, test_users, test_products):
        """Test order serialization to dictionary"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = Order(customer, items, "Credit Card")
        
        # Create payment and delivery
        payment = Payment(order.order_id, "Credit Card")
        delivery = Delivery(order.order_id, "2023-12-31")
        order.payment = payment
        order.delivery = delivery
        
        # Create and apply discount
        discount = Discount("percentage", 0.1)
        order.apply_discount(discount)
        
        order_dict = order.to_dict()
        
        assert order_dict["order_id"] == order.order_id
        assert order_dict["customer_id"] == customer.user_id
        assert order_dict["items"] == items
        assert order_dict["payment_method"] == "Credit Card"
        assert order_dict["payment_id"] == payment.payment_id
        assert order_dict["delivery_id"] == delivery.delivery_id
        assert "discount_applied" in order_dict

# Test Payment class
class TestPayment:
    def test_payment_creation(self):
        """Test payment creation with correct attributes"""
        order_id = str(uuid.uuid4())
        payment = Payment(order_id, "Credit Card")
        
        assert payment.order_id == order_id
        assert payment.method == "Credit Card"
        assert payment.status == "Pending"
        assert hasattr(payment, "payment_id")
    
    def test_payment_process_payment(self):
        """Test payment processing"""
        order_id = str(uuid.uuid4())
        payment = Payment(order_id, "Credit Card")
        
        with patch('builtins.print'):
            result = payment.process_payment()
        
        assert result == True
        assert payment.status == "Completed"
    
    def test_payment_process_payment_different_methods(self):
        """Test payment processing with different methods"""
        payment_methods = ["Credit Card", "PayPal", "Bank Transfer"]
        
        for method in payment_methods:
            order_id = str(uuid.uuid4())
            payment = Payment(order_id, method)
            
            with patch('builtins.print'):
                result = payment.process_payment()
            
            assert result == True
            assert payment.status == "Completed"
    
    def test_payment_to_dict(self):
        """Test payment serialization to dictionary"""
        order_id = str(uuid.uuid4())
        payment = Payment(order_id, "Credit Card")
        payment_dict = payment.to_dict()
        
        assert payment_dict["order_id"] == order_id
        assert payment_dict["method"] == "Credit Card"
        assert payment_dict["status"] == "Pending"
        assert "payment_id" in payment_dict
    
    def test_payment_from_dict(self):
        """Test payment deserialization from dictionary"""
        order_id = str(uuid.uuid4())
        original_payment = Payment(order_id, "Credit Card")
        original_payment.status = "Completed"
        payment_dict = original_payment.to_dict()
        
        new_payment = Payment.from_dict(payment_dict)
        
        assert new_payment.order_id == original_payment.order_id
        assert new_payment.method == original_payment.method
        assert new_payment.status == original_payment.status
        assert new_payment.payment_id == original_payment.payment_id


# Test Delivery class
class TestDelivery:
    def test_delivery_creation(self):
        """Test delivery creation with correct attributes"""
        order_id = str(uuid.uuid4())
        expected_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        delivery = Delivery(order_id, expected_date)
        
        assert delivery.order_id == order_id
        assert delivery.status == "Processing"
        assert delivery.expected_date == expected_date
        assert hasattr(delivery, "delivery_id")
    
    def test_delivery_update_status_valid(self):
        """Test updating delivery status with valid status"""
        order_id = str(uuid.uuid4())
        expected_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        delivery = Delivery(order_id, expected_date)
        
        valid_statuses = ["Processing", "Shipped", "Out for Delivery", "Delivered"]
        
        for status in valid_statuses:
            with patch('builtins.print'):
                delivery.update_status(status)
            assert delivery.status == status
    
    def test_delivery_update_status_invalid(self):
        """Test updating delivery status with invalid status"""
        order_id = str(uuid.uuid4())
        expected_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        delivery = Delivery(order_id, expected_date)
        
        original_status = delivery.status
        
        with patch('builtins.print') as mock_print:
            delivery.update_status("Invalid Status")
        
        assert delivery.status == original_status  # Status should not change
        mock_print.assert_any_call("Invalid status. Valid statuses are: Processing, Shipped, Out for Delivery, Delivered")
    
    def test_delivery_to_dict(self):
        """Test delivery serialization to dictionary"""
        order_id = str(uuid.uuid4())
        expected_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        delivery = Delivery(order_id, expected_date)
        delivery_dict = delivery.to_dict()
        
        assert delivery_dict["order_id"] == order_id
        assert delivery_dict["status"] == "Processing"
        assert delivery_dict["expected_date"] == expected_date
        assert "delivery_id" in delivery_dict
    
    def test_delivery_from_dict(self):
        """Test delivery deserialization from dictionary"""
        order_id = str(uuid.uuid4())
        expected_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        original_delivery = Delivery(order_id, expected_date)
        original_delivery.update_status("Shipped")
        delivery_dict = original_delivery.to_dict()
        
        new_delivery = Delivery.from_dict(delivery_dict)
        
        assert new_delivery.order_id == original_delivery.order_id
        assert new_delivery.status == original_delivery.status
        assert new_delivery.expected_date == original_delivery.expected_date
        assert new_delivery.delivery_id == original_delivery.delivery_id


# Test Discount class
class TestDiscount:
    def test_discount_creation_percentage(self):
        """Test percentage discount creation"""
        discount = Discount("percentage", 0.2)  # 20% discount
        
        assert discount.type == "percentage"
        assert discount.value == 0.2
        assert hasattr(discount, "discount_id")
    
    def test_discount_creation_fixed(self):
        """Test fixed discount creation"""
        discount = Discount("fixed", 50)  # $50 discount
        
        assert discount.type == "fixed"
        assert discount.value == 50
        assert hasattr(discount, "discount_id")
    
    def test_discount_apply_percentage(self):
        """Test applying percentage discount"""
        discount = Discount("percentage", 0.2)  # 20% discount
        original_price = 100
        
        discounted_price = discount.apply_discount(original_price)
        
        assert discounted_price == 80  # 20% off $100 = $80
    
    def test_discount_apply_fixed(self):
        """Test applying fixed discount"""
        discount = Discount("fixed", 30)  # $30 discount
        original_price = 100
        
        discounted_price = discount.apply_discount(original_price)
        
        assert discounted_price == 70  # $100 - $30 = $70
    
    def test_discount_apply_fixed_below_zero(self):
        """Test applying fixed discount that results in negative price"""
        discount = Discount("fixed", 150)  # $150 discount
        original_price = 100
        
        discounted_price = discount.apply_discount(original_price)
        
        assert discounted_price == 0  # Should not go below zero
    
    def test_discount_apply_unknown_type(self):
        """Test applying discount with unknown type"""
        discount = Discount("unknown", 0.2)
        original_price = 100
        
        discounted_price = discount.apply_discount(original_price)
        
        assert discounted_price == original_price  # No discount applied
    
    def test_discount_to_dict(self):
        """Test discount serialization to dictionary"""
        discount = Discount("percentage", 0.2)
        discount_dict = discount.to_dict()
        
        assert discount_dict["type"] == "percentage"
        assert discount_dict["value"] == 0.2
        assert "discount_id" in discount_dict
    
    def test_discount_from_dict(self):
        """Test discount deserialization from dictionary"""
        original_discount = Discount("percentage", 0.2)
        discount_dict = original_discount.to_dict()
        
        new_discount = Discount.from_dict(discount_dict)
        
        assert new_discount.type == original_discount.type
        assert new_discount.value == original_discount.value
        assert new_discount.discount_id == original_discount.discount_id


# Test integration between Payment, Order, and Delivery
class TestIntegration:
    def test_order_payment_integration(self, clean_estore, test_users, test_products):
        """Test integration between order and payment"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        # Customer places an order
        customer.login("password123")
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = customer.place_order(estore, items, "Credit Card")
        
        # Verify payment was created and linked to order
        assert order.payment is not None
        assert order.payment.order_id == order.order_id
        assert order.payment.method == "Credit Card"
        assert order.payment.status == "Completed"  # Payment processed during order placement
    
    def test_order_delivery_integration(self, clean_estore, test_users, test_products):
        """Test integration between order and delivery"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        # Customer places an order
        customer.login("password123")
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = customer.place_order(estore, items, "Credit Card")
        
        # Verify delivery was created and linked to order
        assert order.delivery is not None
        assert order.delivery.order_id == order.order_id
        assert order.delivery.status == "Processing"
        
        # Update delivery status
        order.delivery.update_status("Shipped")
        
        # Verify order tracking reflects delivery status
        tracking_info = order.track_order()
        assert "Delivery status: Shipped" in tracking_info
    
    def test_order_discount_integration(self, clean_estore, test_users, test_products):
        """Test integration between order and discount"""
        estore = clean_estore
        customer = test_users["customer"]
        products = test_products
        
        # Create a discount
        percentage_discount = Discount("percentage", 0.1)  # 10% discount
        fixed_discount = Discount("fixed", 10)  # $10 discount
        
        # Customer places an order
        customer.login("password123")
        items = [{"product_id": products[0].product_id, "quantity": 1}]
        order = customer.place_order(estore, items, "Credit Card")
        
        original_price = order.total_price
        
        # Apply percentage discount
        with patch('builtins.print'):
            order.apply_discount(percentage_discount)
        assert order.total_price == original_price * 0.9
        assert order.discount_applied == percentage_discount
        
        # Apply fixed discount on top
        with patch('builtins.print'):
            order.apply_discount(fixed_discount)
        assert order.total_price == (original_price * 0.9) - 10
        assert order.discount_applied == fixed_discount

# Removed duplicate TestUser class - using the one defined above (lines 104-161)


class TestDelivery:
    def test_delivery_creation(self):
        """Test delivery creation"""
        order_id = str(uuid.uuid4())
        expected_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        delivery = Delivery(order_id, expected_date)
        
        assert delivery.order_id == order_id
        assert delivery.status == "Processing"
        assert isinstance(delivery.expected_date, str)
        
    def test_delivery_update_status(self):
        """Test delivery status update"""
        order_id = str(uuid.uuid4())
        expected_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        delivery = Delivery(order_id, expected_date)
        
        delivery.update_status("Shipped")
        assert delivery.status == "Shipped"
        
        delivery.update_status("Delivered")
        assert delivery.status == "Delivered"


class TestEStore:
    def setup_method(self):
        """Setup common test data"""
        # Reset the singleton instance
        EStore._instance = None
        self.e_store = EStore.get_instance()
        
        # Clear all existing products
        self.e_store.products = []
        
        # Create products correctly with name, category, price, stock
        self.product1 = Product("Teddy Bear", "Electronics", 19.99, 50)
        self.product2 = Product("Doll", "Clothing", 24.99, 30)
        
        # Add products to the store
        self.e_store.add_product(self.product1)
        self.e_store.add_product(self.product2)
        
    def test_store_add_product(self):
        """Test adding product to store"""
        new_product = Product("Toy Car", "Toys", 14.99, 20)
        self.e_store.add_product(new_product)
        
        assert len(self.e_store.products) == 3
        assert new_product in self.e_store.products
        
    def test_store_remove_product(self):
        """Test removing product from store"""
        product_id = self.product1.product_id
        self.e_store.delete_product(product_id)  # Using delete_product instead of remove_product
        
        assert len(self.e_store.products) == 1
        assert self.e_store.get_product(product_id) is None
        assert self.product2 in self.e_store.products
        
    def test_store_get_product(self):
        """Test retrieving product from store"""
        product = self.e_store.get_product(self.product1.product_id)
        
        assert product == self.product1
        assert self.e_store.get_product("nonexistent") is None


if __name__ == "__main__":
    pytest.main(["-v"])