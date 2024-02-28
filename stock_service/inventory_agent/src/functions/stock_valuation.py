import requests

class StockValuation():
    settings = {
        "name": "StockValuation",
        "description": "Retrieve stock valuation",
        "parameters": {
            "type": "object",
            "properties": {
                "num_items": {
                    "type": "integer",
                    "default": 5
                },
            },
            "required": []
        }
    }

    @staticmethod
    def execute(company_name, num_items=5):
        # The URL for the API endpoint
        url = "http://chain-layer:7000/stock-valuation"

        try:
            # Making a GET request to the API with num_items as a query parameter
            params = {'num_items': num_items, 'company_name': company_name}
            response = requests.get(url, params=params)

            # Check if the response is successful
            if response.status_code == 200:
                return {
                    "message": "Successfully retrieved stock valuation",
                    "data": response.json()  # Process the response data as needed
                }
            else:
                return {
                    "message": "Failed to retrieve stock valuation",
                    "data": None,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "message": str(e),
                "data": None
            }
