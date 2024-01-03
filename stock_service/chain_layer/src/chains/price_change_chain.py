import requests
from bson import json_util

API_BASE = "http://data-layer:5000"

class PriceChange():
    def __init__(self, company_name):
        self.company_name = company_name

    def fetch_items(self):
        
        params = {'company_name': self.company_name}

        response = requests.get(f"{API_BASE}/items", json=params)
        
        if response.status_code == 200:
            return json_util.loads(response.json()['data'])
        
        return []

    def update_prices(self, item_id, new_value, is_percentage=False):
        # Update the price of a single item (example: individual update)
        item = self.fetch_item(item_id)
        
        if item:
            current_price = item.get('price', 0)
            
            if is_percentage:
                # Calculate the new price as a percentage change
                new_price = current_price * (1 + (new_value / 100))
            else:
                # Apply the fixed price change
                new_price = current_price + new_value
            
            data = {
                'company_name': self.company_name,
                'item': {
                    'price': new_price  # Specify the new price
                }
            }
            response = requests.put(f"{API_BASE}/items/{item_id}", json=data)
            
            if response.status_code == 200:
                return {"message": "Item price updated successfully"}
        
        return {"error": "Failed to update item price"}

    def fetch_item(self, item_id):
        response = requests.get(f"{API_BASE}/items/{item_id}", json={'company_name': self.company_name})
        
        if response.status_code == 200:
            return json_util.loads(response.json()['data'])
        
        return None

    def execute(self, option, item_id=None, change_value=None, is_percentage=False):
        if option == "update_all" and change_value is not None:
            items = self.fetch_items()
            updated_items = []

            for item in items:
                item_id = item['_id']
                updated_item_result = self.update_prices(item_id, change_value, is_percentage)
                updated_items.append(updated_item_result)

            return updated_items
        elif option == "update_one" and item_id is not None and change_value is not None:
            result = self.update_prices(item_id, change_value, is_percentage)
            return result
        else:
            return [{"error": "Invalid option or missing data"}]

# Example usage:

# # Create an instance of the PriceChange class with your company name
# company_name = "YourCompany"
# price_change_chain = PriceChange(company_name)

# # Example 1: Update prices for all items with a fixed price change
# option = "update_all_prices"
# change_value = 15.0  # Specify the fixed price change
# result = price_change_chain.execute(option, change_value=change_value)
# print(result)

# # Example 2: Update the price of a single item with a percentage change
# option = "update_single_item_price"
# item_id = 3  # Replace with the actual item ID
# percentage_change = 10  # Specify the percentage change
# result = price_change_chain.execute(option, item_id=item_id, change_value=percentage_change, is_percentage=True)
# print(result)

# # Example 3: Update prices for all items from one supplier with a fixed price change
# option = "update_supplier_prices"
# supplier_id = 123  # Replace with the actual supplier ID
# change_value = -5.0  # Specify the fixed price change
# result = price_change_chain.execute(option, supplier_id=supplier_id, change_value=change_value)
# print(result)
