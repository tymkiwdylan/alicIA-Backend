import requests
from bson import json_util

API_BASE = "http://data-layer:5000"

class StockUpdateChain():
    def __init__(self, company_name):
        self.company_name = company_name
        
    def add_item(self, query):
        response = requests.post(f"{API_BASE}/items", json= {'company_name': self.company_name,
                                                             'item': query['item']})
        item_id = json_util.loads(response.json()['data'])
        if response.status_code == 201:
            result = self.update_stock_level(item_id, query)
            return result
        
        return "Something went wrong. Check your inputs and make sure they are valid"
    
    def update_stock_level(self, id, query):
        response = requests.put(f"{API_BASE}/stock-levels/{id}", json = {'company_name': self.company_name,
                                                                         'new_level': query['new_level'] })
        if response.status_code == 200:
            return 'success'
        
        if response.status_code == 500:
            return response.json()['message']
        
        return "Something went wrong. Please try again later or contact support."
    
    def delete_item(self, id):
        response = requests.delete(f"{API_BASE}/items/{id}", json = {'company_name': self.company_name})
        
        if response.status_code == 200:
            return 'success'
        
        if response.status_code == 500:
            return response.json()['message']
        
        return 'Something went wrong. Please try again later or contact support.'
    
    def execute(self, queries):
        
        results = []
        
        for query in queries:
        
            option = query.get('option', 'add')
            id = query.get('id', None)
            
            if option == 'add':
                result = self.add_item(query)
            elif option == 'update':
                if id is None:
                    result = "Item ID is required for update."
                else:
                    result = self.update_stock_level(id, query)
            elif option == 'delete':
                if id is None:
                    result = "Item ID is required for delete."
                else:
                    result = self.delete_item(id)
            else:
                result = "Invalid option. Options available are ['add', 'update', 'delete']"
        
        
        return result
            
