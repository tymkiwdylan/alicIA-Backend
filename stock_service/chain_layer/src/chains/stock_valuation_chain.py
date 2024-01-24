import requests
from bson import json_util

API_BASE = "http://data-layer:5000"

class StockValuation():
    def __init__(self):
        self.company_name = None

    def fetch_items(self):
        params = {'company_name': self.company_name}
        response = requests.get(f"{API_BASE}/items", json=params)
        
        if response.status_code == 200:
            items = self.get_stock_levels(json_util.loads(response.json()['data']))
            return items
        
        return []
    
    def get_stock_levels(self, items):
        
        for item in items:
            response = requests.get(f"{API_BASE}/stock-levels/{item['_id']}", json={'company_name':self.company_name})
            stock = json_util.loads(response.json()['data'])
            item['stock_level'] = stock['current_stock'] if stock != None else 0
        
        return items

    def calculate_total_stock_value(self, items):
        total_value = 0

        for item in items:
            cost_price = item.get('cost', 0)  # Get the cost price from the item object
            total_value += item['stock_level'] * cost_price

        return total_value

    def identify_most_valuable_items(self, items, num_items):
        # Sort items by stock value in descending order
        items.sort(key=lambda x: x['stock_level'] * x.get('cost', 0), reverse=True)

        # Get the top 'num_items' most valuable items
        most_valuable_items = items[:num_items]

        return most_valuable_items

    def execute(self, company_name, num_items=5):
        
        self.company_name = company_name
        
        # Step 1: Fetch all items
        items = self.fetch_items()
        
        if not items:
            return [{"error": "Failed to fetch items"}]

        # Step 2: Calculate the total value of the current stock based on cost prices
        total_stock_value = self.calculate_total_stock_value(items)

        # Step 3: Identify the most valuable items in stock
        most_valuable_items = self.identify_most_valuable_items(items, int(num_items))

        return {
            "total_stock_value": total_stock_value,
            "most_valuable_items": most_valuable_items
        }

# Example usage:

# # Create an instance of the StockValuation class with your company name
# company_name = "YourCompany"
# stock_valuation_chain = StockValuation(company_name)

# # Calculate stock valuation and identify the most valuable items (default: top 5)
# result = stock_valuation_chain.execute()
# print(result)
