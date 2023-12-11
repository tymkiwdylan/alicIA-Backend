from datetime import datetime, timedelta
from . import mongo
from bson import ObjectId
import numpy as np
from sklearn.linear_model import LinearRegression

# Reorder Alerts
def reorder_alerts(company_name):
    alerts = []
    stock_levels = list(mongo.db[f'{company_name}_StockLevels'].find())
    
    for stock in stock_levels:
        if stock['current_stock'] <= stock.get('reorder_point', 0):
            alerts.append({
                'item_id': stock['item_id'],
                'current_stock': stock['current_stock'],
                'reorder_point': stock.get('reorder_point', 0)
            })
    
    return alerts

# Stock Valuation
def stock_valuation(company_name):
    total_value = 0
    items = list(mongo.db[f'{company_name}_Items'].find())
    
    for item in items:
        stock_level = mongo.db[f'{company_name}_StockLevels'].find_one({'item_id': item['_id']})
        if stock_level:
            total_value += item['cost_price'] * stock_level['current_stock']
    
    return total_value

# Stock Forecasting
def stock_forecasting(company_name, item_id, days_ahead=30):
    # Fetch stock movements for the item
    movements = list(mongo.db[f'{company_name}_StockMovements'].find({'item_id': ObjectId(item_id)}))
    
    # Extract dates and quantities from movements
    dates = [movement['date'] for movement in movements]
    quantities = [movement['quantity'] for movement in movements]
    
    # Convert dates to ordinal numbers
    dates_ordinal = [d.toordinal() for d in dates]
    
    # Fit a linear regression model
    model = LinearRegression().fit(np.array(dates_ordinal).reshape(-1, 1), quantities)
    
    # Predict stock for the specified number of days ahead
    future_dates = [(datetime.now() + timedelta(days=i)).toordinal() for i in range(1, days_ahead+1)]
    predictions = model.predict(np.array(future_dates).reshape(-1, 1))
    
    forecast = dict(zip([datetime.fromordinal(d) for d in future_dates], predictions))
    
    return forecast
