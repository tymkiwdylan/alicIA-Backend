from bson import json_util
import requests

API_BASE = "http://data-layer:5000"

class InventoryOverviewChain():
    def __init__(self, company_name):
        self.company_name = company_name

    def fetch_all_items(self):
        items_response = requests.get(f"{API_BASE}/items", json = {'company_name': self.company_name})
        items = items_response.json()['data']
        return json_util.loads(items)

    def fetch_stock_level(self, item_id):
        stock_level_response = requests.get(f"{API_BASE}/stock-levels/{item_id}", json = {'company_name': self.company_name})
        stock_level = stock_level_response.json()['data']
        return json_util.loads(stock_level)

    def analyze_stock_levels(self, stock_level):
        if stock_level == 0:
            return 'Out of stock'
        elif stock_level < 10:
            return 'Low stock'
        else:
            return 'In stock'

    def categorize_items(self, items):
        for item in items:
            stock_level = self.fetch_stock_level(item['_id'])
            item['status'] = self.analyze_stock_levels(stock_level['current_stock'] if stock_level != None else 0)
        return items

    def execute(self):
        items = self.fetch_all_items()
        items = self.categorize_items(items)
        return items
