from ToolGPT import ChatGPTWithFunctions
import openai
import requests
import os
import requests

openai.api_key = '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'



def add_item(company_name, name, sku, description, cost, price):
    """
    Add an item to a company's inventory via API.

    Parameters
    ----------
    company_name : str
        The name of the company.
    name : str
        The name of the item.
    sku : str
        The SKU (Stock Keeping Unit) of the item.
    description : str
        A description of the item.
    cost : float
        The cost of the item.
    price : float
        The selling price of the item.

    Returns
    -------
    str
        A message indicating that the item has been added.
    """
    json_data = {
        'company_name': company_name,
        'item': {
            'name': name,
            'sku': sku,
            'description': description,
            'cost': cost,
            'price': price
        }
    }

    requests.post('http://127.0.0.1:5000/items', json=json_data)

    return "Item añadido"

def get_items(company_name):
    """
    Retrieve a list of items from a company's inventory via API.

    Parameters
    ----------
    company_name : str
        The name of the company.

    Returns
    -------
    list
        A list of items retrieved from the API.
    """
    json = {'company_name': company_name}
    
    response = requests.get('http://127.0.0.1:5000/items', json=json)

    return response.json()['data']



def chat():
    wrapper = ChatGPTWithFunctions()
    functions = [add_item, get_items]

    while True:
        user_input = input("You: ")
        
        # Exit the loop if the user types "exit" or "quit"
        if user_input.lower() in ["exit", "quit"]:
            break

        # Use the ChatGPTWithFunctions wrapper to process user input
        response = wrapper.prompt_with_functions(user_input, functions)

        print("Bot:", response)

if __name__ == "__main__":
    chat()

    
    