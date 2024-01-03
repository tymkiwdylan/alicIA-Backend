import json
import requests
from bson import json_util

API_BASE = "http://data-layer:5000"
class StockSearch():
    def __init__(self, company_name):
        self.company_name = company_name
        
    def search_items(self, query):
        response = requests.get(f"{API_BASE}/items/search", json={'query': query,
                                                                  'company_name': self.company_name})
        
        if response.status_code == 200:
            items = response.json()['data']
            return json_util.loads(items)
        
        return []
    
    def get_item_by_id(self, id):
        try:
            response = requests.get(f"{API_BASE}/items/{id}", json = {'company_name': self.company_name})
            
            if response.status_code == 200:
                return response.json()['data']
        
            return None
        except:
            return None
    
    def fetch_stock_details(self, item):
        print(item['_id'])
        response = requests.get(f"{API_BASE}/stock-levels/{item['_id']}", json={'company_name': self.company_name})
        
        if response.status_code == 200:
            return json_util.loads(response.json()['data'])['current_stock']
        
        return 0
    
    def execute(self, query):
        
        item = self.get_item_by_id(query)
        
        if item != None:
            item['stock_details'] = self.fetch_stock_details(item)

            return [item]
        
        items = self.search_items(query)
        if len(items) > 0:
            for item in items:
                stock_level = self.fetch_stock_details(item)
                item['current_stock'] = stock_level
            
            return items
        
        if item is None:
            return [{"error": "item not found"}]
        else:
            return [{"error": "No items found for the given query"}]
            