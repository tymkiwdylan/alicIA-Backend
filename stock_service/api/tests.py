import requests

# Define the base URL of your Flask app
base_url = 'http://127.0.0.1:5000'  # Replace with the actual URL where your Flask app is running

# Test the /new-stock route
def test_new_stock(company_name):
    data = {'company_name': company_name}
    response = requests.post(f'{base_url}/new-stock', json=data)
    
    if response.status_code == 201:
        print('New stock created successfully')
    else:
        print('Failed to create new stock')
        print(response.status_code, response.text)

# Test the /items (GET) route
def test_get_items(company_name):
    data = {'company_name': company_name}
    response = requests.get(f'{base_url}/items', json=data)
    
    if response.status_code == 200:
        items = response.json()['data']
        print('Items retrieved successfully:')
        print(items)
    else:
        print('Failed to retrieve items')
        print(response.status_code, response.text)

# Test the /items (POST) route
def test_add_item(company_name, item):
    data = {'company_name': company_name, 'item': item}
    response = requests.post(f'{base_url}/items', json=data)
    
    if response.status_code == 201:
        print('Item added successfully')
    else:
        print('Failed to add item')
        print(response.status_code, response.text)

# Define a sample item
sample_item = {
    'name': 'Sample Product',
    'SKU': '12345',
    'description': 'This is a sample product',
    'cost': 10.0,
    'price': 20.0
}

# Test the routes
# test_new_stock('CompanyX')  # Replace with the desired company name
test_add_item('CompanyX', sample_item) 
test_get_items('CompanyX')  # Replace with the desired company name
 # Replace with the desired company name and item
