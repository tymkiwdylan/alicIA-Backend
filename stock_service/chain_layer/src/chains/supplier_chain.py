import requests
from bson import json_util

API_BASE = "http://data-layer:5000"

class SupplierManagement():
    def __init__(self):
        self.company_name = None

    def add_supplier(self, supplier_data):
        supplier_data['company_name'] = self.company_name
        response = requests.post(f"{API_BASE}/suppliers", json=supplier_data)
        
        if response.status_code == 201:
            return {"message": "Supplier added successfully"}
        
        return {"error": "Failed to add supplier"}

    def update_supplier(self, supplier_id, supplier_data):
        supplier_data['company_name'] = self.company_name
        response = requests.put(f"{API_BASE}/suppliers/{supplier_id}", json=supplier_data)
        
        if response.status_code == 200:
            return {"message": "Supplier updated successfully"}
        
        return {"error": "Failed to update supplier"}

    def remove_supplier(self, supplier_id):
        params = {'company_name': self.company_name}
        response = requests.delete(f"{API_BASE}/suppliers/{supplier_id}", json=params)
        
        if response.status_code == 204:
            return {"message": "Supplier removed successfully"}
        
        return {"error": "Failed to remove supplier"}

    def execute(self, company_name, action, data=None):
        
        self.company_name = company_name
        
        if action == "POST" and data:
            result = self.add_supplier(data)
        elif action == "PUT" and data:
            supplier_id = data.get('supplier_id')
            if supplier_id:
                result = self.update_supplier(supplier_id, data)
            else:
                result = {"error": "Supplier ID is required for updating"}
        elif action == "DELETE" and data:
            supplier_id = data.get('supplier_id')
            if supplier_id:
                result = self.remove_supplier(supplier_id)
            else:
                result = {"error": "Supplier ID is required for removal"}
        else:
            result = {"error": "Invalid action or missing data"}

        return result

# Example usage:

# # Create an instance of the SupplierManagement class with your company name
# company_name = "YourCompany"
# supplier_management_chain = SupplierManagement(company_name)

# # Example 1: Add a new supplier
# new_supplier_data = {
#     "supplier_name": "Supplier A",
#     "contact_email": "suppliera@example.com"
# }
# add_supplier_result = supplier_management_chain.execute("add_supplier", data=new_supplier_data)
# print(add_supplier_result)

# # Example 2: Update an existing supplier
# update_supplier_data = {
#     "supplier_id": 123,  # Replace with the actual supplier ID
#     "supplier_name": "Updated Supplier A",
#     "contact_email": "updatedsuppliera@example.com"
# }
# update_supplier_result = supplier_management_chain.execute("update_supplier", data=update_supplier_data)
# print(update_supplier_result)

# # Example 3: Remove a supplier
# remove_supplier_data = {
#     "supplier_id": 123  # Replace with the actual supplier ID
# }
# remove_supplier_result = supplier_management_chain.execute("remove_supplier", data=remove_supplier_data)
# print(remove_supplier_result)

# # Example 4: Send reorder notification
# reorder_notification_data = {
#     "item_id": 456,  # Replace with the actual item ID
#     "supplier_id": 789,  # Replace with the actual supplier ID
#     "reorder_quantity": 50
# }
# reorder_notification_result = supplier_management_chain.execute("notify_reorder", data=reorder_notification_data)
# print(reorder_notification_result)
