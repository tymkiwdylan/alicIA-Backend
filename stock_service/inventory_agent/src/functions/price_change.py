import requests

class PriceChange():
    settings = {
        "name": "PriceChange",
        "description": "Change price of an item or all items",
        "parameters": {
            "type": "object",
            "properties": {
                "option": {
                    "type": "string",
                    "enum": ["update_all", "update_one"]
                },
                "item_id": {
                    "type": "string"
                },
                "change_value": {
                    "type": "number"
                },
                "is_percentage": {
                    "type": "boolean"
                }
            },
            "required": ["option", "item_id", "change_value", "is_percentage"]
        }
    }
    
@staticmethod
def execute(**kwargs):
    url = "http://chain-layer:7000/price"
    try:
        response = requests.put(url, json=kwargs)
        if response.status_code == 200:
            return {
                "message": "Price changed successfully",
                "data": response.json()
            }
        else:
            return {
                "message": "Failed to change price",
                "data": None,
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "message": str(e),
            "data": None
        }