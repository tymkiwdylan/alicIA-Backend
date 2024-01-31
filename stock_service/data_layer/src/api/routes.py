import os
from flask import Blueprint, request, jsonify
from bson import json_util, ObjectId
from . import mongo
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
from .models import *
import pandas as pd
import requests
from requests.auth import HTTPDigestAuth

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

@routes.route('/init-db', methods=['POST'])
def new_stock():
    """
    Create a new set of collections for stock management related to the current user's company.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with a success message or an error message.
    """
    company_name = request.get_json()['company_name']
    
    if company_name:     
        collections_to_create = ['Items', 'StockLevels', 'StockMovements', 'Suppliers', 'Batches', 'Locations']
        
        for collection in collections_to_create:
            mongo.db.create_collection(f'{company_name}_{collection}')
            mongo.db[f'{company_name}_{collection}'].create_index('item_id')
        
        mongo.db[f'{company_name}_Items'].create_index('SKU')
        response = create_search_index(f'{company_name}_Items')
        
        if response.status_code != 200:
            return jsonify(message='Something went wrong. Please try again later or contact support.'), 500
        
        return jsonify(message='Company stock created successfully'), 201
    
    return 'Company not found', 404

def create_search_index(collection_name):
    #Should move keys to .env later
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.atlas.2023-02-01+json'
    }

    response = requests.post(
        'https://cloud.mongodb.com/api/atlas/v2/groups/651c60b6f0266870bf2ef50b/clusters/Stock/fts/indexes',
        headers=headers,
        auth=HTTPDigestAuth('atvnxtkh', 'a50cadb1-955b-45cf-b91e-abcd983e4cab'),
        json={
            "collectionName": collection_name,
            "database": "stock",
            "name": "item_search",
            "mappings": {
                "dynamic": True,
            }
        }
    )   
    
    return response

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
    items = json_util.dumps(items)
    
    return jsonify(message='success', data=items), 200

@routes.route('/items', methods=['POST'])
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

    item_id = mongo.db[f'{company_name}_Items'].insert_one(item).inserted_id
    
    return jsonify(message='Item added successfully', data = json_util.dumps(item_id)), 201

@routes.route('/items/search', methods=['GET'])
def item_search():
    """
    Search the database

    Returns:
        JSON response with the matching items
    """
    query = request.get_json()['query']
    company_name = request.get_json()['company_name']
    
    pipeline = [
        {
        '$search': {
        'index': "item_search",
        'text': {
            'query': query,
            'path': {
            'wildcard': "*"
                    }
                }
            }
        }
    ]
    
    result = list(mongo.db[f'{company_name}_Items'].aggregate(pipeline))    
    result = json_util.dumps(result)
    
    return jsonify(message = 'success', data = result), 200
    
    

@routes.route('/items/<id>', methods=['GET'])
def get_item(id):
    """
    Get information about a specific item by its ID.

    Args:
        id: The ID of the item.

    Returns:
        JSON response with the item information or an error message.
    """
    try:
        company_name = request.get_json()['company_name']
        item = mongo.db[f'{company_name}_Items'].find_one({'_id': ObjectId(id)})
        
        if not item:
            return jsonify(message='Item not found'), 404
        
        item = json_util.dumps(item)
        return jsonify(message='success', data=item), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_items or by searching the item
                       with item_search'''), 500

@routes.route('/items/<id>', methods=['PUT'])
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
    
    try:
        query = {'_id': ObjectId(id)}
        result = mongo.db[f'{company_name}_Items'].update_one(query, {'$set': item_data})
        
        if result.modified_count != 1:
            return jsonify(message='Object not found'), 404
        
        return jsonify(message='Item updated successfully'), 200
    except:
        print(id)
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_items or by searching the item
                       with item_search'''), 500
        

@routes.route('/items/<id>', methods=['DELETE'])
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
    
    try:
    
        result = mongo.db[f'{company_name}_Items'].delete_one({'_id': ObjectId(id)})
        
        if result.deleted_count != 1:
            return jsonify(message='Item not found'), 404
        
        return jsonify(message='Item deleted successfully'), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_items or by searching the item
                       with item_search'''), 500

# Stock Levels routes

@routes.route('/stock-levels', methods=['POST'])  # Changed to POST to accept a list of IDs
def get_stock_levels():
    data = request.get_json()
    company_name = data['company_name']
    ids = data['ids']  # Expecting a list of IDs
    ids = json_util.loads(ids)
    try:
        object_ids = [ObjectId(id) for id in ids]
        query = {'item_id': {'$in': object_ids}}
        stocks = mongo.db[f'{company_name}_StockLevels'].find(query)
        stocks = json_util.dumps(stocks)
        return jsonify(message='success', data=stocks), 200
    except:
        return jsonify(message='Error processing request. Ensure IDs are in the correct format.'), 500

@routes.route('/stock-levels', methods=['PUT'])
def update_stock():
    data = request.get_json()
    company_name = data['company_name']
    updates = json_util.loads(data['updates'])  # Expecting a list of updates (each update is a dict with 'id' and 'new_level')

    bulk_operations = []
    for update in updates:
        try:
            query = {'item_id': ObjectId(update['id'])}
        except Exception as e:
            return jsonify(message=f'Invalid ID format: {str(e)}'), 400

        new_level = {'$set': {'current_stock': update['new_level']}}
        operation = UpdateOne(query, new_level, upsert=True)
        bulk_operations.append(operation)

    if bulk_operations:
        try:
            mongo.db[f'{company_name}_StockLevels'].bulk_write(bulk_operations)
        except BulkWriteError as bwe:
            return jsonify(message=f'Bulk write error: {bwe.details}'), 500
        except Exception as e:
            return jsonify(message=f'Error processing request: {str(e)}'), 500

    return jsonify(message='Stock levels updated successfully'), 200

# Stock Movements routes

@routes.route('/stock-movements', methods=['GET'])
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
def log_stock_movement(): #TODO: record how to record logs and add to bot
    """
    Log a stock movement for a specific company.

    This route is protected and requires a valid JWT for access.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    print(data)
    company_name = data['company_name']
    movement = data['movement']
    mongo.db[f'{company_name}_StockMovements'].insert_one(movement)
    return jsonify(message='Stock movement logged successfully'), 201

# Suppliers routes

@routes.route('/suppliers', methods=['GET'])
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
def get_supplier(supplier_id):
    """
    Get information about a specific supplier by its ID.

    Args:
        supplier_id: The ID of the supplier.

    Returns:
        JSON response with the supplier information or an error message.
    """
    company_name = request.get_json()['company_name']
    try:
        supplier = mongo.db[f'{company_name}_Suppliers'].find_one({'_id': ObjectId(supplier_id)})
        
        if not supplier:
            return jsonify(message='Supplier not found'), 404
        
        serialized_supplier = json_util.dumps(supplier)
        return jsonify(message='success', data=serialized_supplier), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_suppliers'''), 500

@routes.route('/suppliers/<supplier_id>', methods=['PUT'])
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
    try:
        result = mongo.db[f'{company_name}_Suppliers'].update_one({'_id': ObjectId(supplier_id)}, {'$set': supplier_data})
        
        if result.modified_count != 1:
            return jsonify(message='Supplier not found'), 404
        
        return jsonify(message='Supplier updated successfully'), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_suppliers'''), 500

@routes.route('/suppliers/<supplier_id>', methods=['DELETE'])
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
    
    try:
        result = mongo.db[f'{company_name}_Suppliers'].delete_one({'_id': ObjectId(supplier_id)})
        
        if result.deleted_count != 1:
            return jsonify(message='Supplier not found'), 404
        
        return jsonify(message='Supplier deleted successfully'), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_suppliers'''), 500

# Batches routes

@routes.route('/batches/<item_id>', methods=['GET'])
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
    try:
        batches = list(mongo.db[f'{company_name}_Batches'].find({'item_id': ObjectId(item_id)}))
        serialized_batches = json_util.dumps(batches)
        return jsonify(message='success', data=serialized_batches), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_items or by searching the item
                       with item_search'''), 500

@routes.route('/batches', methods=['POST'])
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
    
    try:
        batch['item_id'] = ObjectId(batch['item_id'])
        
        mongo.db[f'{company_name}_Batches'].insert_one(batch)
        return jsonify(message='Batch added successfully'), 201
    except:
        return jsonify(message= '''item_id must be in ObjectID format.
                       You can find the id by calling get_items or by searching the item
                       with item_search'''), 500

@routes.route('/batches/<batch_id>', methods=['PUT'])
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
    try:
        result = mongo.db[f'{company_name}_Batches'].update_one({'_id': ObjectId(batch_id)}, {'$set': batch_data})
        
        if result.modified_count != 1:
            return jsonify(message='Batch not found'), 404
        
        return jsonify(message='Batch updated successfully'), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_batches'''), 500

@routes.route('/batches/<batch_id>', methods=['DELETE'])
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
    try:
        result = mongo.db[f'{company_name}_Batches'].delete_one({'_id': ObjectId(batch_id)})
        
        if result.deleted_count != 1:
            return jsonify(message='Batch not found'), 404
        
        return jsonify(message='Batch deleted successfully'), 204
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_batches'''), 500

# Locations routes

@routes.route('/locations', methods=['GET'])
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
def get_location(location_id):
    """
    Get information about a specific location by its ID.

    Args:
        location_id: The ID of the location.

    Returns:
        JSON response with the location information or an error message.
    """
    company_name = request.get_json()['company_name']
    
    try:
        location = mongo.db[f'{company_name}_Locations'].find_one({'_id': ObjectId(location_id)})
        
        if not location:
            return jsonify(message='Location not found'), 404
        
        serialized_location = json_util.dumps(location)
        return jsonify(message='success', data=serialized_location), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_locations'''), 500

@routes.route('/locations/<location_id>', methods=['PUT'])
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
    try:
        result = mongo.db[f'{company_name}_Locations'].update_one({'_id': ObjectId(location_id)}, {'$set': location_data})
        
        if result.modified_count != 1:
            return jsonify(message='Location not found'), 404
        
        return jsonify(message='Location updated successfully'), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_locations'''), 500

@routes.route('/locations/<location_id>', methods=['DELETE'])
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
    try:
        result = mongo.db[f'{company_name}_Locations'].delete_one({'_id': ObjectId(location_id)})
        
        if result.deleted_count != 1:
            return jsonify(message='Location not found'), 404
        
        return jsonify(message='Location deleted successfully'), 200
    except:
        return jsonify(message= '''id must be in ObjectID format.
                       You can find the id by calling get_locations'''), 500


@routes.route('/load-from-file', methods=['POST'])
def load_products():
    file = request.files.get('file')
    company_name = request.form.get('company_name')
    print(company_name)
    
    # Check the file extension
    filename, file_extension = os.path.splitext(file.filename)
    
    # Read the file using pandas
    if file_extension == '.csv':
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    
    # Check for missing columns
    required_columns = ['name', 'SKU', 'description', 'cost', 'price', 'stock_level']
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        return jsonify({'error': f'Missing columns: {", ".join(missing_columns)}'}), 400

    # Preparing bulk operations for items
    items_operations = []
    sku_to_stock_level = {}
    for _, row in df.iterrows():
        item = {
        "name": row['name'],
        "SKU": row['SKU'],
        "description": row['description'] if not pd.isnull(row['description']) else "",
        "cost": int(row['cost']) if not pd.isnull(row['cost']) else 0,
        "price": int(row['price'])
        }
        sku_to_stock_level[item['SKU']] = int(row['stock_level']) if not pd.isnull(row['stock_level']) else 0
        items_operations.append(UpdateOne({'SKU': item['SKU']}, {'$set': item}, upsert=True))

    # Execute bulk write operations for items
    if items_operations:
        mongo.db[f'{company_name}_Items'].bulk_write(items_operations)

    # Handle small datasets without batch processing
    total_entries = len(df)
    if total_entries <= 5:
        # Directly process each entry
        for sku, stock_level in sku_to_stock_level.items():
            item_id = mongo.db[f'{company_name}_Items'].find_one({'SKU': sku})['_id']
            mongo.db[f'{company_name}_StockLevels'].update_one(
                {'item_id': item_id},
                {'$set': {'current_stock': stock_level}},
                upsert=True
            )
    else:
        # Dynamic Batch Size Calculation for larger datasets
        batch_size = max(50, min(500, total_entries // 5))
        skus = list(sku_to_stock_level.keys())
        stock_level_operations = []

        for i in range(0, len(skus), batch_size):
            batch_skus = skus[i:i + batch_size]
            items = mongo.db[f'{company_name}_Items'].find({'SKU': {'$in': batch_skus}})
            
            sku_to_id = {item['SKU']: item['_id'] for item in items}
            for sku, item_id in sku_to_id.items():
                stock_level_operations.append(UpdateOne(
                    {'item_id': item_id}, 
                    {'$set': {'current_stock': sku_to_stock_level[sku]}}, 
                    upsert=True
                ))

        # Execute bulk write operations for stock levels
        if stock_level_operations:
            mongo.db[f'{company_name}_StockLevels'].bulk_write(stock_level_operations)

    return jsonify(message='Success'), 200