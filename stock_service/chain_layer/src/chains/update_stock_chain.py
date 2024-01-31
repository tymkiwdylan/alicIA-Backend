import requests
from bson import json_util, ObjectId

API_BASE = "http://data-layer:5000"

class StockUpdateChain():
    def __init__(self):
        self.company_name = None

    def add_item(self, item):
        response = requests.post(f"{API_BASE}/items", json={'company_name': self.company_name, 'item': item})
        if response.status_code == 201:
            return json_util.loads(response.json()['data'])
        else:
            return None

    def update_stock_level(self, stock_updates):
        response = requests.put(f"{API_BASE}/stock-levels", json={'company_name': self.company_name, 'updates': stock_updates})
        return response.status_code == 200

    def delete_item(self, id):
        response = requests.delete(f"{API_BASE}/items/{id}", json={'company_name': self.company_name})
        return response.status_code == 200

    def execute(self, company_name, queries):
        self.company_name = company_name
        results = []

        stock_updates = []
        for query in queries:
            option = query.get('option', 'add')
            if option == 'add':
                item_id = self.add_item(query.get('item', {}))
                if item_id:
                    stock_updates.append({'id': str(item_id), 'new_level': query.get('new_level', 0)})
                    results.append(f"Item added with ID: {item_id}")
                else:
                    results.append("Failed to add item")
            elif option in ['update', 'delete']:
                item_id = query.get('id')
                if item_id:
                    if option == 'update':
                        stock_updates.append({'id': item_id, 'new_level': query.get('new_level', 0)})
                    else:
                        result = self.delete_item(item_id)
                        results.append('Item deleted successfully' if result else 'Failed to delete item')
                else:
                    results.append("Item ID is required for update/delete")

        if stock_updates:
            update_success = self.update_stock_level(stock_updates)
            results.append('Stock levels updated successfully' if update_success else 'Failed to update stock levels')

        return results
