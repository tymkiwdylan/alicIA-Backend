import requests
from bson import json_util

API_BASE = "http://data-layer:5000"

class StockValuation:
    def __init__(self):
        self.company_name = None

    def fetch_items(self):
        params = {'company_name': self.company_name}
        response = requests.get(f"{API_BASE}/items", json=params)
        
        if response.status_code == 200:
            return json_util.loads(response.json()['data'])
        else:
            return []

    def fetch_stock_levels(self, item_ids):
        response = requests.post(f"{API_BASE}/stock-levels", json={'company_name': self.company_name, 'ids': item_ids})
        if response.status_code == 200:
            stock_levels = response.json()['data']
            return {level['item_id']: level for level in json_util.loads(stock_levels)}
        else:
            return {}

    def get_stock_levels(self, items):
        item_ids = json_util.dumps([item['_id'] for item in items])
        stock_levels = self.fetch_stock_levels(item_ids)

        for item in items:
            item_id = item['_id']
            stock_level_info = stock_levels.get(item_id, {'current_stock': 0})
            item['stock_level'] = stock_level_info['current_stock']
        
        return items

    def calculate_total_stock_value(self, items):
        total_value = 0
        for item in items:
            cost_price = item.get('cost', 0)
            total_value += item['stock_level'] * cost_price
        return total_value

    def identify_most_valuable_items(self, items, num_items):
        items.sort(key=lambda x: x['stock_level'] * x.get('cost', 0), reverse=True)
        most_valuable_items = items[:num_items]
        return most_valuable_items

    def execute(self, company_name, num_items=5):
        self.company_name = company_name
        items = self.fetch_items()
        if not items:
            return {"error": "Failed to fetch items"}

        items_with_stock = self.get_stock_levels(items)
        total_stock_value = self.calculate_total_stock_value(items_with_stock)
        most_valuable_items = self.identify_most_valuable_items(items_with_stock, int(num_items))

        return {
            "total_stock_value": total_stock_value,
            "most_valuable_items": most_valuable_items
        }

# Example usage:
# stock_valuation_chain = StockValuation()
# stock_valuation_chain.company_name = "YourCompanyName"
# result = stock_valuation_chain.execute(num_items=5)
# print(result)
