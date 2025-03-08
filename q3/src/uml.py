from graphviz import Digraph

dot = Digraph('DollMart_UML_Class_Diagram', format='png')

# User Class
dot.node('User', '''{User|
- user_id: str \l
- name: str \l
- email: str \l
- password: str \l
- is_logged_in: bool \l |
+ login(password: str) -> bool \l
+ logout() -> None \l
+ to_dict() -> Dict \l
+ from_dict(data: Dict) -> User \l
}''', shape='record')

# Customer Class
dot.node('Customer', '''{Customer|
- order_history: List[str] \l |
+ place_order(e_store: EStore, items: List[Dict], payment_method: str) -> Optional[Order] \l
+ view_order_history(e_store: EStore) -> None \l
+ get_discount() -> float \l
+ to_dict() -> Dict \l
+ from_dict(data: Dict) -> Customer \l
}''', shape='record')

# RetailStore Class
dot.node('RetailStore', '''{RetailStore|
- store_name: str \l
- business_id: str \l |
+ apply_bulk_discount() -> float \l
+ to_dict() -> Dict \l
+ from_dict(data: Dict) -> RetailStore \l
}''', shape='record')

# Admin Class
dot.node('Admin', '''{Admin|
+ manage_products(e_store: EStore) -> None \l
+ view_orders(e_store: EStore) -> None \l
+ manage_delivery(e_store: EStore) -> None \l
}''', shape='record')

# Product Class
dot.node('Product', '''{Product|
- product_id: str \l
- name: str \l
- category: str \l
- price: float \l
- stock: int \l |
+ update_stock(quantity_change: int) -> None \l
+ apply_discount(discount_percentage: float) -> float \l
+ to_dict() -> Dict \l
+ from_dict(data: Dict) -> Product \l
}''', shape='record')

# Order Class
dot.node('Order', '''{Order|
- order_id: str \l
- customer: Customer \l
- items: List[Dict] \l
- payment_method: str \l
- status: str \l
- total_price: float \l
- date: str \l
- discount_applied: Optional[Discount] \l
- payment: Optional[Payment] \l
- delivery: Optional[Delivery] \l |
+ calculate_total() -> float \l
+ apply_discount(discount: Discount) -> None \l
+ track_order() -> str \l
+ to_dict() -> Dict \l
}''', shape='record')

# Payment Class
dot.node('Payment', '''{Payment|
- payment_id: str \l
- order_id: str \l
- method: str \l
- status: str \l |
+ process_payment() -> bool \l
+ to_dict() -> Dict \l
+ from_dict(data: Dict) -> Payment \l
}''', shape='record')

# Delivery Class
dot.node('Delivery', '''{Delivery|
- delivery_id: str \l
- order_id: str \l
- status: str \l
- expected_date: str \l |
+ update_status(new_status: str) -> None \l
+ to_dict() -> Dict \l
+ from_dict(data: Dict) -> Delivery \l
}''', shape='record')

# Discount Class
dot.node('Discount', '''{Discount|
- discount_id: str \l
- type: str \l
- value: float \l |
+ apply_discount(price: float) -> float \l
+ to_dict() -> Dict \l
+ from_dict(data: Dict) -> Discount \l
}''', shape='record')

# EStore Class
dot.node('EStore', '''{EStore|
- users: List[User] \l
- products: List[Product] \l
- orders: List[Order] \l
- discounts: List[Discount] \l
- payments: List[Payment] \l
- deliveries: List[Delivery] \l |
+ get_instance() -> EStore \l
+ search_product(query: str) -> List[Product] \l
+ add_product(product: Product) -> None \l
+ get_product(product_id: str) -> Optional[Product] \l
+ delete_product(product_id: str) -> bool \l
+ get_order(order_id: str) -> Optional[Order] \l
+ process_order(order: Order) -> None \l
+ get_user(email: str) -> Optional[User] \l
+ add_user(user: User) -> None \l
+ save_data() -> None \l
+ load_data() -> None \l
}''', shape='record')

# Relationships
dot.edge('Customer', 'User', arrowhead='onormal', label='inherits')
dot.edge('Admin', 'User', arrowhead='onormal', label='inherits')
dot.edge('RetailStore', 'User', arrowhead='onormal', label='inherits')

dot.edge('Order', 'Customer', arrowhead='onormal', label='placed by')
dot.edge('Order', 'Product', arrowhead='onormal', label='contains')
dot.edge('Order', 'Payment', arrowhead='onormal', label='has')
dot.edge('Order', 'Delivery', arrowhead='onormal', label='delivered by')
dot.edge('Order', 'Discount', arrowhead='onormal', label='applies')

dot.edge('EStore', 'User', arrowhead='onormal', label='manages')
dot.edge('EStore', 'Product', arrowhead='onormal', label='has')
dot.edge('EStore', 'Order', arrowhead='onormal', label='processes')
dot.edge('EStore', 'Payment', arrowhead='onormal', label='handles')
dot.edge('EStore', 'Delivery', arrowhead='onormal', label='tracks')

# Render the diagram
dot.render('DollMart_UML_Class_Diagram', format='png', view=True)

