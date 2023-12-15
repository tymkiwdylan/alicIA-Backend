#!/bin/bash

# Pull code 
git pull -f

source myvenv/bin/activate

# Start API 1
nohup python stock_service/data_layer/app.py

nohup python stock_service/chain_layer/main.py

# Start API 3
nohup python3 customer_service/main.py

# Start ngrok
nohup ngrok start --all

echo "All APIs and Ngrok started."
