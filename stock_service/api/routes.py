from flask import Blueprint, request, jsonify
from bson import json_util, ObjectId
from . import mongo
from .models import *
from flask_jwt_extended import jwt_required, get_jwt_identity

routes = Blueprint('routes', __name__)

@routes.errorhandler(500)
def internal_error(error):
    """
    Handle internal server errors (HTTP status code 500).

    Args:
        error: The error object.

    Returns:
        JSON response with an error message and status code 500.
    """
    return jsonify(message="Internal Server Error"), 500

@routes.route('/new-stock', methods=['POST'])
@jwt_required()
def new_stock():
    """
    Create a new set of collections for stock management related to the current user's company.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with a success message or an error message.
    """
    current_user = User.query.filter_by(username=get_jwt_identity()).first()
    
    if current_user:
        company_name = current_user.company_name
        
        collections_to_create = ['Items', 'StockLevels', 'StockMovements', 'Suppliers', 'Batches', 'Locations']
        
        for collection in collections_to_create:
            mongo.db.create_collection(f'{company_name}_{collection}')
            mongo.db[f'{company_name}_{collection}'].create_index('item_id')
        
        return jsonify(message='Company stock created successfully'), 201
    
    return 'Company not found', 404

# Items routes

@routes.route('/items', methods=['GET'])
def get_items():
    """
    Get a list of items for a specific company.

    Returns:
        JSON response with the list of items or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    
    items = list(mongo.db[f'{company_name}_Items'].find())
    serialized_items = json_util.dumps(items)
    
    return jsonify(message='success', data=serialized_items), 200

@routes.route('/items', methods=['POST'])
@jwt_required()
def add_item():
    """
    Add a new item to a company's inventory.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    item = data['item']
    quantity = data['quantity']
    
    item_id = mongo.db[f'{company_name}_Items'].insert_one(item).inserted_id
    mongo.db[f'{company_name}_StockLevels'].insert_one({'item_id': item_id, 'current_stock': quantity})
    
    return jsonify(message='Item added successfully'), 201

@routes.route('/items/<id>', methods=['GET'])
def get_item(id):
    """
    Get information about a specific item by its ID.

    Args:
        id: The ID of the item.

    Returns:
        JSON response with the item information or an error message.
    """
    company_name = request.get_json()['company_name']
    item = mongo.db[f'{company_name}_Items'].find_one({'_id': ObjectId(id)})
    
    if not item:
        return jsonify(message='Item not found'), 404
    
    item = json_util.dumps(item)
    return jsonify(message='success', data=item), 200

@routes.route('/items/<id>', methods=['PUT'])
@jwt_required()
def update_item(id):
    """
    Update information about a specific item by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        id: The ID of the item to update.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    item_data = data['item']
    
    query = {'_id': ObjectId(id)}
    result = mongo.db[f'{company_name}_Items'].update_one(query, {'$set': item_data})
    
    if result.modified_count != 1:
        return jsonify(message='Object not found'), 404
    
    return jsonify(message='Item updated successfully'), 200

@routes.route('/items/<id>', methods=['DELETE'])
@jwt_required()
def delete_item(id):
    """
    Delete a specific item by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        id: The ID of the item to delete.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    
    result = mongo.db[f'{company_name}_Items'].delete_one({'_id': ObjectId(id)})
    
    if result.deleted_count != 1:
        return jsonify(message='Item not found'), 404
    
    return jsonify(message='Item deleted successfully'), 200

# Stock Levels routes

@routes.route('/stock-levels/<id>', methods=['GET'])
@jwt_required()
def get_stock_levels(id):
    """
    Get the stock levels for a specific item by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        id: The ID of the item.

    Returns:
        JSON response with the stock levels or an error message.
    """
    company_name = request.get_json()['company_name']
    stock = mongo.db[f'{company_name}_StockLevels'].find_one({'item_id': ObjectId(id)})
    
    stock = json_util.dumps(stock)
    return jsonify(message='success', data=stock), 200

@routes.route('/stock-levels/<id>', methods=['PUT'])
@jwt_required()
def update_stock(id):
    """
    Update the stock level for a specific item by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        id: The ID of the item.
    
    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    new_level = data['new_level']
    
    query = {'item_id': ObjectId(id)}
    update = {'$set': {'current_stock': new_level}}
    
    # TODO: Implement concurrency checks or use transactions if multiple operations can update stock simultaneously
    mongo.db[f'{company_name}_StockLevels'].update_one(query, update)
    
    return jsonify(message='Stock level updated successfully'), 200

# Stock Movements routes

@routes.route('/stock-movements', methods=['GET'])
@jwt_required()
def get_stock_movements():
    """
    Get a list of stock movements for a specific company.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with the list of stock movements or an error message.
    """
    company_name = request.get_json()['company_name']
    movements = list(mongo.db[f'{company_name}_StockMovements'].find())
    serialized_movements = json_util.dumps(movements)
    return jsonify(message='success', data=serialized_movements), 200

@routes.route('/stock-movements', methods=['POST'])
@jwt_required()
def log_stock_movement():
    """
    Log a stock movement for a specific company.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    movement = data['movement']
    mongo.db[f'{company_name}_StockMovements'].insert_one(movement)
    return jsonify(message='Stock movement logged successfully'), 201

# Suppliers routes

@routes.route('/suppliers', methods=['GET'])
@jwt_required()
def get_suppliers():
    """
    Get a list of suppliers for a specific company.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with the list of suppliers or an error message.
    """
    company_name = request.get_json()['company_name']
    suppliers = list(mongo.db[f'{company_name}_Suppliers'].find())
    serialized_suppliers = json_util.dumps(suppliers)
    return jsonify(message='success', data=serialized_suppliers), 200

@routes.route('/suppliers', methods=['POST'])
@jwt_required()
def add_supplier():
    """
    Add a new supplier to a company's list of suppliers.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    supplier = data['supplier']
    mongo.db[f'{company_name}_Suppliers'].insert_one(supplier)
    return jsonify(message='Supplier added successfully'), 201

@routes.route('/suppliers/<supplier_id>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_id):
    """
    Get information about a specific supplier by its ID.

    Args:
        supplier_id: The ID of the supplier.

    Returns:
        JSON response with the supplier information or an error message.
    """
    company_name = request.get_json()['company_name']
    supplier = mongo.db[f'{company_name}_Suppliers'].find_one({'_id': ObjectId(supplier_id)})
    
    if not supplier:
        return jsonify(message='Supplier not found'), 404
    
    serialized_supplier = json_util.dumps(supplier)
    return jsonify(message='success', data=serialized_supplier), 200

@routes.route('/suppliers/<supplier_id>', methods=['PUT'])
@jwt_required()
def update_supplier(supplier_id):
    """
    Update information about a specific supplier by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        supplier_id: The ID of the supplier to update.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    supplier_data = data['supplier']
    result = mongo.db[f'{company_name}_Suppliers'].update_one({'_id': ObjectId(supplier_id)}, {'$set': supplier_data})
    
    if result.modified_count != 1:
        return jsonify(message='Supplier not found'), 404
    
    return jsonify(message='Supplier updated successfully'), 200

@routes.route('/suppliers/<supplier_id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(supplier_id):
    """
    Delete a specific supplier by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        supplier_id: The ID of the supplier to delete.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    result = mongo.db[f'{company_name}_Suppliers'].delete_one({'_id': ObjectId(supplier_id)})
    
    if result.deleted_count != 1:
        return jsonify(message='Supplier not found'), 404
    
    return jsonify(message='Supplier deleted successfully'), 200

# Batches routes

@routes.route('/batches/<item_id>', methods=['GET'])
@jwt_required()
def get_batches(item_id):
    """
    Get a list of batches for a specific item by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        item_id: The ID of the item.

    Returns:
        JSON response with the list of batches or an error message.
    """
    company_name = request.get_json()['company_name']
    batches = list(mongo.db[f'{company_name}_Batches'].find({'item_id': ObjectId(item_id)}))
    serialized_batches = json_util.dumps(batches)
    return jsonify(message='success', data=serialized_batches), 200

@routes.route('/batches', methods=['POST'])
@jwt_required()
def add_batch():
    """
    Add a new batch of items to a company's inventory.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    batch = data['batch']
    mongo.db[f'{company_name}_Batches'].insert_one(batch)
    return jsonify(message='Batch added successfully'), 201

@routes.route('/batches/<batch_id>', methods=['PUT'])
@jwt_required()
def update_batch(batch_id):
    """
    Update information about a specific batch by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        batch_id: The ID of the batch to update.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    batch_data = data['batch']
    result = mongo.db[f'{company_name}_Batches'].update_one({'_id': ObjectId(batch_id)}, {'$set': batch_data})
    
    if result.modified_count != 1:
        return jsonify(message='Batch not found'), 404
    
    return jsonify(message='Batch updated successfully'), 200

@routes.route('/batches/<batch_id>', methods=['DELETE'])
@jwt_required()
def delete_batch(batch_id):
    """
    Delete a specific batch by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        batch_id: The ID of the batch to delete.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    result = mongo.db[f'{company_name}_Batches'].delete_one({'_id': ObjectId(batch_id)})
    
    if result.deleted_count != 1:
        return jsonify(message='Batch not found'), 404
    
    return jsonify(message='Batch deleted successfully'), 200

# Locations routes

@routes.route('/locations', methods=['GET'])
@jwt_required()
def get_locations():
    """
    Get a list of locations for a specific company.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with the list of locations or an error message.
    """
    company_name = request.get_json()['company_name']
    locations = list(mongo.db[f'{company_name}_Locations'].find())
    serialized_locations = json_util.dumps(locations)
    return jsonify(message='success', data=serialized_locations), 200

@routes.route('/locations', methods=['POST'])
@jwt_required()
def add_location():
    """
    Add a new location to a company's list of locations.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    location = data['location']
    mongo.db[f'{company_name}_Locations'].insert_one(location)
    return jsonify(message='Location added successfully'), 201

@routes.route('/locations/<location_id>', methods=['GET'])
@jwt_required()
def get_location(location_id):
    """
    Get information about a specific location by its ID.

    Args:
        location_id: The ID of the location.

    Returns:
        JSON response with the location information or an error message.
    """
    company_name = request.get_json()['company_name']
    location = mongo.db[f'{company_name}_Locations'].find_one({'_id': ObjectId(location_id)})
    
    if not location:
        return jsonify(message='Location not found'), 404
    
    serialized_location = json_util.dumps(location)
    return jsonify(message='success', data=serialized_location), 200

@routes.route('/locations/<location_id>', methods=['PUT'])
@jwt_required()
def update_location(location_id):
    """
    Update information about a specific location by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        location_id: The ID of the location to update.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    location_data = data['location']
    result = mongo.db[f'{company_name}_Locations'].update_one({'_id': ObjectId(location_id)}, {'$set': location_data})
    
    if result.modified_count != 1:
        return jsonify(message='Location not found'), 404
    
    return jsonify(message='Location updated successfully'), 200

@routes.route('/locations/<location_id>', methods=['DELETE'])
@jwt_required()
def delete_location(location_id):
    """
    Delete a specific location by its ID.

    This route is protected and requires a valid JWT for access.

    Args:
        location_id: The ID of the location to delete.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    company_name = data['company_name']
    result = mongo.db[f'{company_name}_Locations'].delete_one({'_id': ObjectId(location_id)})
    
    if result.deleted_count != 1:
        return jsonify(message='Location not found'), 404
    
    return jsonify(message='Location deleted successfully'), 200
