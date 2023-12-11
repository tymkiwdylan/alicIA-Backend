import requests
from bson import json_util

API_BASE = "http://127.0.0.1:5000"

class StockMovementTracking():
    def __init__(self, company_name):
        self.company_name = company_name

    def log_stock_movement(self, movement_data):
        movement_data['company_name'] = self.company_name
        response = requests.post(f"{API_BASE}/stock-movements", json=movement_data)
        
        if response.status_code == 201:
            return {"message": "Stock movement logged successfully"}
        
        return {"error": "Failed to log stock movement"}

    def get_stock_movements(self):
        params = {'company_name': self.company_name}
        response = requests.get(f"{API_BASE}/stock-movements", json=params)
        
        if response.status_code == 200:
            return json_util.loads(response.json()['data'])
        
        return {"error": "Failed to fetch stock movements log"}

    def execute(self, movement_data=None):
        if movement_data is not None:
            result = self.log_stock_movement(movement_data)
        else:
            result = self.get_stock_movements()

        return result

# # Example usage:

# # Create an instance of the StockMovementTracking class with your company name
# company_name = "YourCompany"
# stock_movement_chain = StockMovementTracking(company_name)

# # Log a new stock movement
# new_movement_data = {
#     "item_id": 123,
#     "movement_type": "in",
#     "quantity": 50
# }
# log_result = stock_movement_chain.execute(movement_data=new_movement_data)
# print(log_result)

# # Fetch the log of all stock movements
# movements_log = stock_movement_chain.execute()
# print(movements_log)
