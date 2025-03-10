# Project -:Food Delivery System

## 1. System Overview

The Food Delivery System is a comprehensive platform that connects customers, restaurants, and delivery agents. It enables customers to browse menus, place orders, and track deliveries, while providing restaurant managers with tools to manage menus and orders, and allowing delivery agents to handle deliveries efficiently.

## 2. User Roles

- **Customer**: End users who browse menus and place food orders.
- **Restaurant Manager**: Staff responsible for menu management and order processing.
- **Delivery Agent**: Personnel who deliver orders to customers.
- **Admin**: System administrators with full access to manage users and system operations.

## 3. Functional Requirements

### 3.1 User Management

- User registration with role-based access control.
- Authentication system with username/password.


### 3.2 Menu Management

- Add, update, and remove menu items.
- Categorize menu items.
- Set pricing and descriptions.
- View complete menu.

### 3.3 Order Management

- Place orders (delivery or takeaway).
- View order history.
- Track order status in real-time.
- Cancel orders.
- Calculate total order amount.

### 3.4 Delivery Management

- Assign delivery agents to orders.
- Track delivery status.
- Calculate estimated delivery times.
- Manage delivery agent availability.

### 3.5 Reporting and Analytics

- View order statistics.
- Track delivery performance.
- Monitor popular menu items.

## 4. Non-Functional Requirements

### 4.1 Performance

- Process order requests within 3 seconds.
- Support multiple concurrent users.

### 4.2 Security

- Secure user authentication.
- Role-based access control.
- Data encryption for sensitive information.

### 4.3 Reliability

- System available 99.9% of the time.
- Data persistence across sessions.
- Error handling and recovery mechanisms.

### 4.4 Usability

- Intuitive command-line interface.
- Clear navigation between different functions.
- Informative error messages.

## 5. Data Model

### 5.1 User

- **ID**, username, password, name, role.

### 5.2 Menu Item

- **ID**, name, description, price, category.

### 5.3 Order

- **ID**, customer ID, items, total amount, status, order type, delivery address, created timestamp.

### 5.4 Delivery Agent

- **ID**, name, status, current order.

## 6. Major Use Cases

### 6.1 Customer Use Cases

#### 6.1.1 Browse Menu

- **Primary Actor**: Customer
- **Description**: Customer views the restaurant menu with items grouped by categories.
- **Preconditions**: Customer is logged in.
- **Flow**:
  1. Customer selects "View Menu" option.
  2. System displays all menu items organized by categories.
  3. Customer can view item details including name, description, and price.
- **Alternate Flows**:
  1. System displays "No menu items available" message if the menu is empty.
  2. If categories are inconsistent, the system displays items without categorization.
  3. If menu retrieval fails, the system shows an error message and returns to the main menu.
- **Post Condition**: Customer views the menu items.
- **Release**: R1

#### 6.1.2 Place Order

- **Primary Actor**: Customer
- **Description**: Customer creates a new food order.
- **Preconditions**: Customer is logged in, menu items exist.
- **Flow**:
  1. Customer selects "Place Order" option.
  2. System displays the menu.
  3. Customer adds items to cart with quantities.
  4. Customer selects order type (delivery/takeaway).
  5. For delivery orders, customer provides delivery address.
  6. System calculates total amount.
  7. System confirms order placement.
  8. For delivery orders, system assigns a delivery agent.
  9. System provides estimated delivery/pickup time.
- **Alternate Flows**:
  1. System prevents order submission with an empty cart and prompts the customer to add items.
  2. System requests valid input if the customer enters a negative/zero quantity.
  3. System notifies the customer and offers a takeaway option if no agents are available.
  4. System requests a valid delivery address if the input is incomplete.
  5. System allows the customer to try an alternative payment method or cancel the order.
  6. System saves the order draft and allows continuation when the connection is restored.
- **Post Condition**: Order is placed and confirmed.
- **Release**: R1

#### 6.1.3 Track Order

- **Primary Actor**: Customer
- **Description**: Customer tracks the status of their order.
- **Preconditions**: Customer has placed an order.
- **Flow**:
  1. Customer selects "Track Order" option.
  2. Customer enters order ID.
  3. System displays current order status.
  4. System shows estimated time remaining for delivery/pickup.
- **Alternate Flows**:
  1. System displays "Order not found" message if the ID doesn't exist.
  2. System shows the cancellation reason and refund status for cancelled orders.
  3. System displays cached order status if real-time tracking is unavailable.
- **Post Condition**: Customer views the current status of their order.
- **Release**: R1

#### 6.1.4 View Order History

- **Primary Actor**: Customer
- **Description**: Customer views their past orders.
- **Preconditions**: Customer is logged in.
- **Flow**:
  1. Customer selects "View My Orders" option.
  2. System displays all orders placed by the customer.
  3. Customer can view order details including items, quantities, prices, and status.
- **Alternate Flows**:
  1. System displays "No previous orders found" message.
  2. System displays all orders without filters if filtering fails.
  3. System implements pagination for customers with extensive order history.
- **Post Condition**: Customer views their order history.
- **Release**: R1

### 6.2 Restaurant Manager Use Cases

#### 6.2.1 View All Orders

- **Primary Actor**: Restaurant Manager
- **Description**: Manager views all orders in the system.
- **Preconditions**: Manager is logged in.
- **Flow**:
  1. Manager selects "View All Orders" option.
  2. System displays all orders with their ID, date, status, and total amount.
- **Alternate Flows**:
  1. System displays "No orders in the system" message.
  2. System shows all orders if the filter operation fails.
  3. System implements pagination for handling a large number of orders.
- **Post Condition**: Manager views all orders.
- **Release**: R2

#### 6.2.2 Update Order Status

- **Primary Actor**: Restaurant Manager
- **Description**: Manager updates the status of an order.
- **Preconditions**: Manager is logged in, order exists.
- **Flow**:
  1. Manager selects "Update Order Status" option.
  2. Manager enters order ID.
  3. System displays current order status.
  4. Manager selects new status.
  5. System updates order status and confirms change.
- **Alternate Flows**:
  1. System shows an error message if the order doesn't exist.
  2. System prevents illogical status changes (e.g., PLACED to DELIVERED).
  3. System notifies if the order already has the requested status.
  4. System prevents status updates for cancelled orders.
- **Post Condition**: Order status is updated.
- **Release**: R2

#### 6.2.3 Manage Menu Items

- **Primary Actor**: Restaurant Manager
- **Description**: Manager adds, updates, or removes menu items.
- **Preconditions**: Manager is logged in.
- **Flow**:
  1. Manager selects "Manage Menu" option.
  2. Manager chooses to add, update, or remove a menu item.
  3. For adding: Manager enters item details (name, description, price, category).
  4. For updating: Manager selects item and updates relevant fields.
  5. For removing: Manager selects item and confirms deletion.
  6. System confirms the operation.
- **Alternate Flows**:
  1. System requests a different name if an item with the same name exists.
  2. System rejects negative or zero prices with an error message.
  3. System warns before removing items currently in orders.
  4. System handles gracefully if an image upload fails for menu items.
- **Post Condition**: Menu items are managed.
- **Release**: R2

### 6.3 Delivery Agent Use Cases

#### 6.3.1 View Assigned Orders

- **Primary Actor**: Delivery Agent
- **Description**: Delivery agent views the list of orders assigned to them.
- **Preconditions**: Delivery agent is logged in.
- **Flow**:
  1. Delivery agent selects "View My Assigned Orders" option.
  2. System displays all orders assigned to the delivery agent.
  3. Delivery agent can view order details including customer information, delivery address, and order status.
- **Alternate Flows**:
  1. System displays "No orders assigned" message.
  2. System shows cached data if real-time data is unavailable.
- **Post Condition**: Delivery agent views assigned orders.
- **Release**: R3

#### 6.3.2 Update Delivery Status

- **Primary Actor**: Delivery Agent
- **Description**: Delivery agent updates the status of an assigned order.
- **Preconditions**: Delivery agent is logged in, order is assigned to the agent.
- **Flow**:
  1. Delivery agent selects "Update Delivery Status" option.
  2. Delivery agent enters order ID.
  3. System displays current order status.
  4. Delivery agent selects new status (e.g., Out for Delivery, Delivered).
  5. System updates order status and confirms the change.
- **Alternate Flows**:
  1. System explains valid status transitions if an invalid update is attempted.
  2. System provides options (call customer, wait, return order) if the customer is unavailable.
  3. System handles order cancellation during the delivery process.
  4. System allows manual status updates if GPS tracking is unavailable.
- **Post Condition**: Delivery status is updated.
- **Release**: R3

### 6.4 Admin Use Cases

#### 6.4.1 Register Staff

- **Primary Actor**: Admin
- **Description**: Admin registers new staff members (Restaurant Manager, Delivery Agent, Admin).
- **Preconditions**: Admin is logged in.
- **Flow**:
  1. Admin selects "Register New Staff" option.
  2. Admin enters staff details (username, password, full name, role).
  3. System registers the new staff member and confirms the registration.
- **Alternate Flows**:
  1. System requests a different username if the current one is taken.
  2. System displays valid role options if an invalid role is selected.
  3. System explains password requirements if the input doesn't meet criteria.
  4. System logs error details and allows retry.
- **Post Condition**: New staff member is registered.
- **Release**: R4

#### 6.4.2 View All Delivery Agents

- **Primary Actor**: Admin
- **Description**: Admin views all registered delivery agents.
- **Preconditions**: Admin is logged in.
- **Flow**:
  1. Admin selects "View All Delivery Agents" option.
  2. System displays all delivery agents with their ID, name, status, and current order (if any).
- **Alternate Flows**:
  1. System displays "No delivery agents registered" message.
  2. System shows all agents if filtering fails.
  3. System provides an interface for reassigning orders if an agent becomes unavailable.
- **Post Condition**: Admin views all delivery agents.
- **Release**: R4

## 7. System Architecture

The system follows a layered architecture:

- **Presentation Layer**: CLI interface.
- **Business Logic Layer**: User, menu, order, and delivery management.
- **Data Storage Layer**: JSON-based persistent storage.

## 8. System Requirements

### 8.1 Software Requirements

- Operating System: Windows, macOS, or Linux.
- Python 3.8 or higher.
- Required Python libraries: `json`, `os`, `time`, `uuid`, `datetime`, `enum`, `random`.
- Git for version control.

## 9. Users Profile

### 9.1 Customer

- **Profile**: General public with basic computer skills.
- **Mode**: Browsing menus, placing orders, tracking orders, and viewing order history.

### 9.2 Restaurant Manager

- **Profile**: Restaurant staff with moderate computer skills.
- **Mode**: Managing menus, viewing and updating orders.

### 9.3 Delivery Agent

- **Profile**: Delivery personnel with basic computer skills.
- **Mode**: Viewing assigned orders, updating delivery status.

### 9.4 Admin

- **Profile**: System administrators with advanced computer skills.
- **Mode**: Managing users, viewing delivery agents, and overall system maintenance.

## 10. Integration Points

- Data persistence through file system (JSON).
- Potential for future integration with payment gateways, SMS notifications, etc.

## 11. Constraints and Limitations

- CLI-based interface limits user experience.
- No real-time push notifications.
- Limited scalability with file-based storage.
