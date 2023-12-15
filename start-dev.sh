#!/bin/bash

# Pull code 
cd /sis/Smart-Integrated-System/
git pull -f

source myvenv/bin/activate

# Start API 1
cd data_layer/
nohup python app.py

cd chain_layer/
nohup python main.py

# Start API 3
cd /sis/Smart-Integrated-System/customer_service/
nohup python3 main.py 

# Start ngrok
nohup ngrok start --all

echo "All APIs and Ngrok started."
