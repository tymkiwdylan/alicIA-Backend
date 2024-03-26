import requests
from bson import json_util

API_BASE = "http://data-layer:5000"

class BatchManagement():
    def __init__(self):
        self.company_name = None

    def add_new_batch(self, batch_data):
        # Send a request to add a new batch (POST /batches)
        data = {
            'company_name': self.company_name,
            'batch_data': batch_data
        }
        response = requests.post(f"{API_BASE}/batches", json=data)
        
        if response.status_code == 201:
            return response.json()['data']
        
        return None

    def update_batch(self, batch_id, updated_batch_data):
        # Send a request to update a batch (PUT /batches/{batch_id})
        data = {
            'company_name': self.company_name,
            'batch_data': updated_batch_data
        }
        response = requests.put(f"{API_BASE}/batches/{batch_id}", json=data)
        
        if response.status_code == 200:
            return response.json()['data']
        
        return None

    def remove_batch(self, batch_id):
        # Send a request to remove a batch (DELETE /batches/{batch_id})
        params = {'company_name': self.company_name}
        response = requests.delete(f"{API_BASE}/batches/{batch_id}", params=params)
        
        if response.status_code == 204:
            return {"message": "Batch removed successfully"}
        
        return None

    def execute(self, company_name, operation, batch_id=None, batch_data=None, updated_batch_data=None):
        self.company_name = company_name
        if operation == "POST" and batch_data:
            return self.add_new_batch(batch_data)
        elif operation == "PUT" and batch_id and updated_batch_data:
            return self.update_batch(batch_id, updated_batch_data)
        elif operation == "DELETE" and batch_id:
            return self.remove_batch(batch_id)
        else:
            return [{"error": "Invalid operation or missing data"}]

# Example usage:

# # Create an instance of the BatchManagement class with your company name
# company_name = "YourCompany"
# batch_management_chain = BatchManagement(company_name)

# # Example 1: Add a new batch
# operation = "add_new_batch"
# batch_data = {
#     'batch_name': "New Batch",
#     'items': [1, 2, 3],  # List of item IDs in the batch
# }
# result = batch_management_chain.execute(operation, batch_data=batch_data)
# print(result)

# # Example 2: Update a batch
# operation = "update_batch"
# batch_id = 123  # Replace with the actual batch ID
# updated_batch_data = {
#     'batch_name': "Updated Batch",
#     'items': [4, 5, 6],  # Updated list of item IDs in the batch
# }
# result = batch_management_chain.execute(operation, batch_id=batch_id, updated_batch_data=updated_batch_data)
# print(result)

# # Example 3: Remove a batch
# operation = "remove_batch"
# batch_id = 123  # Replace with the actual batch ID
# result = batch_management_chain.execute(operation, batch_id=batch_id)
# print(result)

# # Example 4: Update stock levels of an item
# operation = "update_stock_levels"
# item_id = 7  # Replace with the actual item ID
# new_stock_level = 50  # Specify the new stock level
# result = batch_management_chain.execute(operation, item_id=item_id, new_stock_level=new_stock_level)
# print(result)
