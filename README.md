# Food Delivery System

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
- Profile management.
- Session management.

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
- **Main Flow**:
  1. Customer selects "View Menu" option.
  2. System displays all menu items organized by categories.
  3. Customer can view item details including name, description, and price.

#### 6.1.2 Place Order

- **Primary Actor**: Customer
- **Description**: Customer creates a new food order.
- **Preconditions**: Customer is logged in, menu items exist.
- **Main Flow**:
  1. Customer selects "Place Order" option.
  2. System displays the menu.
  3. Customer adds items to cart with quantities.
  4. Customer selects order type (delivery/takeaway).
  5. For delivery orders, customer provides delivery address.
  6. System calculates total amount.
  7. System confirms order placement.
  8. For delivery orders, system assigns a delivery agent.
  9. System provides estimated delivery/pickup time.

#### 6.1.3 Track Order

- **Primary Actor**: Customer
- **Description**: Customer tracks the status of their order.
- **Preconditions**: Customer has placed an order.
- **Main Flow**:
  1. Customer selects "Track Order" option.
  2. Customer enters order ID.
  3. System displays current order status.
  4. System shows estimated time remaining for delivery/pickup.

#### 6.1.4 View Order History

- **Primary Actor**: Customer
- **Description**: Customer views their past orders.
- **Preconditions**: Customer is logged in.
- **Main Flow**:
  1. Customer selects "View My Orders" option.
  2. System displays all orders placed by the customer.
  3. Customer can view order details including items, quantities, prices, and status.

### 6.2 Restaurant Manager Use Cases

#### 6.2.1 View All Orders

- **Primary Actor**: Restaurant Manager
- **Description**: Manager views all orders in the system.
- **Preconditions**: Manager is logged in.
- **Main Flow**:
  1. Manager selects "View All Orders" option.
  2. System displays all orders with their ID, date, status, and total amount.

#### 6.2.2 Update Order Status

- **Primary Actor**: Restaurant Manager
- **Description**: Manager updates the status of an order.
- **Preconditions**: Manager is logged in, order exists.
- **Main Flow**:
  1. Manager selects "Update Order Status" option.
  2. Manager enters order ID.
  3. System displays current order status.
  4. Manager selects new status.
  5. System updates order status and confirms change.

#### 6.2.3 Manage Menu Items

- **Primary Actor**: Restaurant Manager
- **Description**: Manager adds, updates, or removes menu items.
- **Preconditions**: Manager is logged in.
- **Main Flow**:
  1. Manager selects "Manage Menu" option.
  2. Manager chooses to add, update, or remove a menu item.
  3. For adding: Manager enters item details (name, description, price, category).
  4. For updating: Manager selects item and updates relevant fields.
  5. For removing: Manager selects item and confirms deletion.
  6. System confirms the operation.

## 7. System Architecture

The system follows a layered architecture:

- **Presentation Layer**: CLI interface.
- **Business Logic Layer**: User, menu, order, and delivery management.
- **Data Storage Layer**: JSON-based persistent storage.

## 8. Integration Points

- Data persistence through file system (JSON).
- Potential for future integration with payment gateways, SMS notifications, etc.

## 9. Constraints and Limitations

- CLI-based interface limits user experience.
- No real-time push notifications.
- Limited scalability with file-based storage.
- No authentication tokens or password encryption.
  """
