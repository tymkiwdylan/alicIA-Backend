import requests
import datetime  # for date calculations
from bson import json_util

API_BASE = "http://data-layer:5000"

class ReorderAlerts():
    def __init__(self):
        self.company_name = None

    def monitor_stock_levels(self):
        response = requests.get(f"{API_BASE}/stock-levels", json={'company_name': self.company_name})
        
        if response.status_code == 200:
            return json_util.loads(response.json()['data'])
        
        return []

    def get_batches_for_item(self, item_id):
        response = requests.get(f"{API_BASE}/batches/{item_id}")
        
        if response.status_code == 200:
            return json_util.loads(response.json()['data'])
        
        return []

    def generate_reorder_alerts(self, items, reorder_point):
        reorder_alerts = []

        for item in items:
            batches = self.get_batches_for_item(item['item_id'])
            if item['stock_level'] <= reorder_point or self.check_batch_expiration(batches):
                reorder_alerts.append({
                    'item_id': item['item_id'],
                    'item_name': item['item_name'],
                    'stock_level': item['stock_level'],
                    'reorder_point': reorder_point,
                    'expiration_alert': self.check_batch_expiration(batches)
                })

        return reorder_alerts

    def check_batch_expiration(self, batches):
        current_date = datetime.date.today()
        expiration_alert = False

        for batch in batches:
            expiration_date = datetime.datetime.strptime(batch['expiration_date'], "%Y-%m-%d").date()
            if expiration_date <= current_date:
                expiration_alert = True
                break

        return expiration_alert

    def execute(self, company_name, reorder_point):
        self.company_name = company_name
        
        stock_levels = self.monitor_stock_levels()
        
        if not stock_levels:
            return [{"error": "Failed to retrieve stock levels"}]

        reorder_alerts = self.generate_reorder_alerts(stock_levels, reorder_point)

        if not reorder_alerts:
            return [{"message": "No items require reordering or have impending expiration"}]

        # We could make this a post request to a webhook to send notifications
        return reorder_alerts
