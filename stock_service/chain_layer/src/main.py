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

stock_search = StockSearch()
inventory_overview = InventoryOverviewChain()
price_change = PriceChange()
stock_tracking = StockMovementTracking()
valuation = StockValuation()
batch_manager = BatchManagement()
reorder_alerts = ReorderAlerts()
supplier_manager = SupplierManagement()
stock_update = StockUpdateChain()


app = Flask(__name__)

@app.route('/search', methods = ['GET'])
def search_item():
    query = request.args.get('query')
    company_name = request.args.get('company_name')
    
    result = stock_search.execute(company_name, query)
    
    return jsonify(data = json_util.dumps(result)), 200

@app.route('/overview', methods = ['GET'])
def overview():
    company_name = request.args.get('company_name')
    inventory_summary = inventory_overview.execute(company_name=company_name) 
    return jsonify(message = 'success', data = json_util.dumps(inventory_summary)), 200

@app.route('/price', methods = ['PUT'])
def change_price():
    data = request.get_json()
    
    company_name = data['company_name']
    option = data.get('option')
    item_id = data.get('item_id', None)
    change_value = data.get('change_value', None)
    is_percentage = data.get('is_percentage', False)
    
    result = price_change.execute(company_name, option, item_id, change_value, is_percentage)
    
    return jsonify(data = result), 200

@app.route('/movement-log', methods = ['GET'])
def get_movements():
    
    company_name = request.args.get('company_name')
    
    return jsonify(message = 'success', data = json_util.dumps(stock_tracking.execute(company_name))), 200

@app.route('/movement-log', methods = ['POST'])
def log_movement():
    data = request.get_json()
    movement_data = data
    company_name = data['company_name']
    
    return jsonify( data= stock_tracking.execute(company_name=company_name, movement_data = movement_data)), 200

@app.route('/stock-valuation', methods = ['GET'])
def get_valuation():
    num_items = request.args.get('num_items', 5)
    company_name = request.args.get('company_name')
    return jsonify(message = 'success', data = json_util.dumps(valuation.execute(company_name, num_items))), 200

@app.route('/batch', methods = ['POST', 'PUT', 'DELETE'])
def batch_manangement():
    data = request.get_json()
    company_name = data['company_name']
    operation = request.method
    
    if operation == 'POST':
        batch_data = data['batch_data']
        return batch_manager.execute(company_name, operation, batch_data = batch_data)
    
    if operation == 'PUT':
        batch_id = data['batch_id']
        updated_batch_data = data['update_data']
        
        return batch_manager.execute(company_name, operation, batch_id=batch_id, updated_batch_data=updated_batch_data)
    
    if operation == 'DELETE':
        batch_id = data['batch_id']
        
        return jsonify(data = batch_manager.execute(company_name, operation, batch_id=batch_id)), 200
    

@app.route('/reorder-alert', methods = ['GET'])
def reorder_alert():
    reorder_point = request.args.get('reorder_point')
    company_name = request.args.get('company_name')
    
    return jsonify(data = json_util.dumps(reorder_alerts.execute(company_name, reorder_point=reorder_point))), 200

@app.route('/supplier', methods = ['POST', 'PUT', 'DELETE'])
def supplier():
    data = request.get_json()
    supplier_data = data['supplier_data']
    company_name = data['company_name']
    operation = request.method
    return jsonify(data = supplier_manager.execute(company_name, operation, supplier_data)), 200

@app.route('/stock', methods = ['POST'])
def stock_management():
    query = request.get_json()['queries']
    company_name = request.get_json()['company_name']
    
    return jsonify( data= stock_update.execute(company_name, query)), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)