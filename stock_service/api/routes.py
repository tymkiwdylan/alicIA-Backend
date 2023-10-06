from flask import Blueprint, request
from bson import json_util, ObjectId
from . import mongo
from .models import *

routes = Blueprint('routes', __name__)

@routes.route('/new-stock', methods=['POST'])
def new_stock():
    '''
    Creates all collections for a new stock.
    
    Params:
        company_name
    '''
    data = request.get_json(force=True)
    
    company_name = data['company_name']
    
    # Create collections with the company-specific prefix
    collections_to_create = ['Items', 'StockLevels', 'StockMovements',
                             'Suppliers', 'Batches', 'Locations']
    
    for collection in collections_to_create:
        mongo.db.create_collection(f'{company_name}_{collection}')
        mongo.db[f'{company_name}_{collection}'].create_index('item_id')
    
    return 'Company stock created succesfully', 201

# Items requests

@routes.route('/items', methods=['GET'])
def get_items():
    '''
    Returns all the items of a company
    
    Params:
        company_name
    
    Returns:
        A list with all items
    '''
    
    data = request.get_json()
    
    company_name = data['company_name']
    
    items = list(mongo.db[f'{company_name}_Items'].find())
    
    serialized_items = json_util.dumps(items)
    
    return {'message' : 'success', 'data': serialized_items}, 200

@routes.route('/items', methods=['POST'])
def add_items():
    '''
        Adds an item to the items collection of a company
        
        Params:
            company_name: String 
            item: Item
    '''

    data = request.get_json()
    
    company_name = data['company_name']
    item = data['item']
    
    new_item = Item(**item)
    
    mongo.db[f'{company_name}_Items'].insert_one(new_item.__dict__)
    
    return 'Item added succesfully', 201
    
@routes.route('/items/<id>', methods=['GET'])
def get_item(id):
    '''
        Get a specific item
        
        Params:
            id: id of the item to retrieve
        Returns:
            item
    '''
    
    company_name = request.get_json()['company_name'] #To change once we set up auth
    
    item = mongo.db[f'{company_name}_Items'].find_one({'_id': ObjectId(id)})
    
    if not item:
        return {'message' : 'Item not found'}, 404
    
    item = json_util.dumps(item)
    
    return {'message' : 'success', 'data': item}, 200

@routes.route('/items/<id>', methods=['PUT'])
def update_item(id):
    data = request.get_json()
    
    company_name = data['company_name']
    item_data = data['item']
    
    query = {'_id': ObjectId(id)}
    
    result = mongo.db[f'{company_name}_Items'].update_one(query, {'$set': item_data})
    
    if result.modified_count != 1:
        return 'Object not found', 404
    
    return 'Item updated succesfully', 200

    
    


    