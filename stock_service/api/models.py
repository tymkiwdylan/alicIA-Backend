class Item:
    def __init__(self, name, SKU, description, cost, price):
        self.name = name
        self.SKU = SKU
        self.description = description
        self.cost = cost
        self.price = price
        
class StockLevels:
    def __init__(self, item_id, current_stock):
        self.item_id = item_id
        self.current_stock = current_stock

class StockMovement:
    def __init__(self, item_id, movement_type, quantity, timestamp):
        self.item_id = item_id
        self.movement_type = movement_type
        self.quantity = quantity
        self.timestamp = timestamp

class Supplier:
    def __init__(self, name, contact_details, items_supplied):
        self.name = name
        self.contact_details = contact_details
        self.items_supplied = items_supplied  # List of item IDs supplied by this supplier

class Batch:
    def __init__(self, item_id, manufacturing_date, expiry_date):
        self.item_id = item_id
        self.manufacturing_date = manufacturing_date
        self.expiry_date = expiry_date

