import unittest
from ..src.classes import UserManager, UserRole, MenuManager, OrderManager, DeliveryManager, OrderType, OrderStatus

class TestFoodDeliverySystem(unittest.TestCase):

    def setUp(self):
        """ Initialize fresh instances before each test """
        self.user_manager = UserManager()
        self.menu_manager = MenuManager()
        self.order_manager = OrderManager()
        self.delivery_manager = DeliveryManager()

    ### 🧑-------------------------------------------------------USER MANAGEMENT TESTS ----------------------------------------##
    def test_register_user(self):
        success, message = self.user_manager.register_user("test_user", "password123", UserRole.CUSTOMER, "Test User")
        self.assertTrue(success)
        self.assertEqual(message, "User registered successfully")

    def test_duplicate_user_registration(self):
        self.user_manager.register_user("test_user", "password123", UserRole.CUSTOMER, "Test User")
        success, message = self.user_manager.register_user("test_user", "password123", UserRole.CUSTOMER, "Test User")
        self.assertFalse(success)
        self.assertEqual(message, "Username already exists")

    def test_authenticate_valid_user(self):
        self.user_manager.register_user("test_user", "password123", UserRole.CUSTOMER, "Test User")
        success, user = self.user_manager.authenticate("test_user", "password123")
        self.assertTrue(success)
        self.assertEqual(user.username, "test_user")

    def test_authenticate_invalid_user(self):
        success, message = self.user_manager.authenticate("nonexistent_user", "password")
        self.assertFalse(success)
        self.assertEqual(message, "User not found")

    ### 🍕 MENU MANAGEMENT TESTS ###
    def test_add_menu_item(self):
        item = self.menu_manager.add_item("Burger", "Delicious cheeseburger", 8.99, "Fast Food")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Burger")

    def test_update_menu_item(self):
        item = self.menu_manager.add_item("Burger", "Delicious cheeseburger", 8.99, "Fast Food")
        success, message = self.menu_manager.update_item(item.id, name="Veggie Burger", price=9.99)
        self.assertTrue(success)
        updated_item = self.menu_manager.get_item(item.id)
        self.assertEqual(updated_item.name, "Veggie Burger")
        self.assertEqual(updated_item.price, 9.99)

    def test_remove_menu_item(self):
        item = self.menu_manager.add_item("Burger", "Delicious cheeseburger", 8.99, "Fast Food")
        success, message = self.menu_manager.remove_item(item.id)
        self.assertTrue(success)
        self.assertIsNone(self.menu_manager.get_item(item.id))

    ### 🛒 ORDER MANAGEMENT TESTS ###
    def test_create_order(self):
        self.user_manager.register_user("customer1", "password", UserRole.CUSTOMER, "John Doe")
        success, user = self.user_manager.authenticate("customer1", "password")
        self.assertTrue(success)

        item = self.menu_manager.add_item("Pizza", "Cheese Pizza", 10.99, "Main Course")
        cart = [{"item_id": item.id, "quantity": 2}]

        success, order = self.order_manager.create_order(user.id, cart, OrderType.DELIVERY, "123 Street")
        self.assertTrue(success)
        self.assertEqual(order.customer_id, user.id)
        self.assertEqual(order.items[0]["name"], "Pizza")

    def test_get_customer_orders(self):
        self.user_manager.register_user("customer2", "password", UserRole.CUSTOMER, "Alice")
        success, user = self.user_manager.authenticate("customer2", "password")
        self.assertTrue(success)

        item = self.menu_manager.add_item("Sushi", "Salmon Sushi", 12.99, "Japanese")
        cart = [{"item_id": item.id, "quantity": 1}]

        self.order_manager.create_order(user.id, cart, OrderType.TAKEAWAY)
        orders = self.order_manager.get_customer_orders(user.id)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].items[0]["name"], "Sushi")

    def test_update_order_status(self):
        self.user_manager.register_user("customer3", "password", UserRole.CUSTOMER, "Bob")
        success, user = self.user_manager.authenticate("customer3", "password")
        self.assertTrue(success)

        item = self.menu_manager.add_item("Pasta", "Creamy Alfredo", 9.99, "Italian")
        cart = [{"item_id": item.id, "quantity": 1}]

        success, order = self.order_manager.create_order(user.id, cart, OrderType.DELIVERY, "456 Avenue")
        self.assertTrue(success)

        success, message = self.order_manager.update_order_status(order.id, OrderStatus.CONFIRMED)
        self.assertTrue(success)
        updated_order = self.order_manager.get_order(order.id)
        self.assertEqual(updated_order.status, OrderStatus.CONFIRMED)

    ### 🚚 DELIVERY MANAGEMENT TESTS ###
    def test_assign_delivery_agent(self):
        self.user_manager.register_user("delivery1", "password", UserRole.DELIVERY_AGENT, "Agent 1")

        self.user_manager.register_user("customer4", "password", UserRole.CUSTOMER, "Carol")
        success, user = self.user_manager.authenticate("customer4", "password")
        self.assertTrue(success)

        item = self.menu_manager.add_item("Fries", "Crispy Fries", 3.99, "Sides")
        cart = [{"item_id": item.id, "quantity": 1}]

        success, order = self.order_manager.create_order(user.id, cart, OrderType.DELIVERY, "789 Boulevard")
        self.assertTrue(success)

        success, agent_id = self.delivery_manager.assign_delivery_agent(order.id)
        self.assertTrue(success)
        self.assertIsNotNone(agent_id)

    def test_get_agent_orders(self):
        self.user_manager.register_user("agent2", "password", UserRole.DELIVERY_AGENT, "Agent 2")
        success, agent = self.user_manager.authenticate("agent2", "password")
        self.assertTrue(success)

        self.user_manager.register_user("customer5", "password", UserRole.CUSTOMER, "David")
        success, user = self.user_manager.authenticate("customer5", "password")
        self.assertTrue(success)

        item = self.menu_manager.add_item("Taco", "Spicy Taco", 5.99, "Mexican")
        cart = [{"item_id": item.id, "quantity": 2}]

        success, order = self.order_manager.create_order(user.id, cart, OrderType.DELIVERY, "1020 Street")
        self.assertTrue(success)

        success, agent_id = self.delivery_manager.assign_delivery_agent(order.id)
        self.assertTrue(success)

        agent_orders = self.delivery_manager.get_agent_orders(agent_id)
        self.assertEqual(len(agent_orders), 1)
        self.assertEqual(agent_orders[0].items[0]["name"], "Taco")

if __name__ == "__main__":
    unittest.main()
