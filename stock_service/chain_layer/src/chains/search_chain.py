import requests
from bson import json_util, ObjectId

API_BASE = "http://data-layer:5000"

class StockSearch():
    def __init__(self):
        self.company_name = None

    def search_items(self, query):
        response = requests.get(f"{API_BASE}/items/search", json={'query': query, 'company_name': self.company_name})
        
        if response.status_code == 200:
            items = response.json()['data']
            return json_util.loads(items)
        
        return []
    
    def get_item_by_id(self, id):
        try:
            response = requests.get(f"{API_BASE}/items/{id}", json={'company_name': self.company_name})
            
            if response.status_code == 200:
                return response.json()['data']
        
            return None
        except:
            return None
    
    def fetch_stock_details(self, items):
        item_ids = json_util.dumps([item['_id'] for item in items])
        response = requests.post(f"{API_BASE}/stock-levels", json={'company_name': self.company_name, 'ids': item_ids})
        
        if response.status_code == 200:
            stock_levels = response.json()['data']
            stock_levels_dict = {level['item_id']: level for level in json_util.loads(stock_levels)}
            return stock_levels_dict
        else:
            return {item_id: 0 for item_id in item_ids}
    
    def execute(self, company_name, query):
        self.company_name = company_name

        # Search by ID first
        item = self.get_item_by_id(query)
        if item:
            item['stock_details'] = self.fetch_stock_details([item])
            return [item]
        
        # If not found by ID, perform a search
        items = self.search_items(query)
        print(items)
        if items:
            stock_levels_dict = self.fetch_stock_details(items)
            for item in items:
                item['current_stock'] = stock_levels_dict.get(item['_id'], 0)
            return items

        return [{"error": "No items found for the given query"}]
