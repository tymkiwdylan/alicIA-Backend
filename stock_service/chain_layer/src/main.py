from flask import Flask, request, jsonify
from chains.search_chain import StockSearch
from chains.inventory_chain import InventoryOverviewChain
from chains.price_change_chain import PriceChange
from chains.stock_movement_chain import StockMovementTracking
from chains.stock_valuation_chain import StockValuation
from chains.batch_management_chain import BatchManagement
from chains.reorder_chain import ReorderAlerts
from chains.supplier_chain import SupplierManagement
from chains.update_stock_chain import StockUpdateChain
from bson import json_util

company = 'CompanyX'

stock_search = StockSearch(company)
inventory_overview = InventoryOverviewChain(company)
price_change = PriceChange(company)
stock_tracking = StockMovementTracking(company)
valuation = StockValuation(company)
batch_manager = BatchManagement(company)
reorder_alerts = ReorderAlerts(company)
supplier_manager = SupplierManagement(company)
stock_update = StockUpdateChain(company)


app = Flask(__name__)

@app.route('/search', methods = ['GET'])
def search_item():
    query = request.args.get('query')
    
    result = stock_search.execute(query)
    
    return jsonify(data = json_util.dumps(result))

@app.route('/overview', methods = ['GET'])
def overview():
    inventory_summary = inventory_overview.execute() 
    return jsonify(message = 'success', data = json_util.dumps(inventory_summary))

@app.route('/price', methods = ['PUT'])
def change_price():
    data = request.get_json()
    
    option = data.get('option')
    item_id = data.get('item_id', None)
    change_value = data.get('change_value', None)
    is_percentage = data.get('is_percentage', False)
    
    return price_change.execute(option, item_id, change_value, is_percentage)

@app.route('/movement-log', methods = ['GET'])
def get_movements():
    
    return jsonify(message = 'success', data = json_util.dumps(stock_tracking.execute()))

@app.route('/movement-log', methods = ['POST'])
def log_movement():
    data = request.get_json()
    movement_data = data
    
    return stock_tracking.execute(movement_data = movement_data)

@app.route('/stock-valuation', methods = ['GET'])
def get_valuation():
    num_items = request.args.get('num_items', 5)
    
    return jsonify(message = 'success', data = json_util.dumps(valuation.execute(num_items)))

@app.route('/batch', methods = ['POST', 'PUT', 'DELETE'])
def batch_manangement():
    data = request.get_json()
    operation = request.method
    
    if operation == 'POST':
        batch_data = data['batch_data']
        return batch_manager.execute(operation, batch_data = batch_data)
    
    if operation == 'PUT':
        batch_id = data['batch_id']
        updated_batch_data = data['update_data']
        
        return batch_manager.execute(operation, batch_id=batch_id, updated_batch_data=updated_batch_data)
    
    if operation == 'DELETE':
        batch_id = data['batch_id']
        
        return batch_manager.execute(operation, batch_id=batch_id)
    

@app.route('/reorder-alert', methods = ['GET'])
def reorder_alert():
    reorder_point = request.args.get('reorder_point')
    
    return json_util.dumps(reorder_alerts.execute(reorder_point=reorder_point))

@app.route('/supplier', methods = ['POST', 'PUT', 'DELETE'])
def supplier():
    data = request.get_json()
    supplier_data = data['supplier_data']
    operation = request.method
    return supplier_manager.execute(operation, supplier_data)

@app.route('/stock', methods = ['POST'])
def stock_management():
    query = request.get_json()['queries']
    
    return stock_update.execute(query)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)