from bson import json_util
import requests

API_BASE = "http://data-layer:5000"

class InventoryOverviewChain():
    def __init__(self):
        self.company_name = None

    def fetch_all_items(self):
        items_response = requests.get(f"{API_BASE}/items", json={'company_name': self.company_name})
        items = items_response.json()['data']
        return json_util.loads(items)

    def fetch_stock_levels(self, item_ids):
        stock_levels_response = requests.post(f"{API_BASE}/stock-levels", json={'company_name': self.company_name, 'ids': item_ids})
        stock_levels = stock_levels_response.json()['data']
        return {level['item_id']: level for level in json_util.loads(stock_levels)}

    def analyze_stock_level(self, stock_level):
        if stock_level == 0:
            return 'Fuera de stock'
        elif stock_level < 10:
            return 'Stock bajo'
        else:
            return 'En stock'

    def categorize_items(self, items):
        item_ids = json_util.dumps([item['_id'] for item in items])
        stock_levels = self.fetch_stock_levels(item_ids)

        for item in items:
            item_id = item['_id']
            stock_level = stock_levels.get(item_id, {'current_stock': 0})['current_stock']
            item['status'] = self.analyze_stock_level(stock_level)
        return items

    def execute(self, company_name):
        self.company_name = company_name
        items = self.fetch_all_items()
        items = self.categorize_items(items)
        return items
