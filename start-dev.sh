#!/bin/bash

# Pull code 
cd /sis/Smart-Integrated-System/
git pull -f

# Start API 1
cd /sis/Smart-Integrated-System/stock_service/
nohup python app.py

# Start API 3
cd /sis/Smart-Integrated-System/customer_service/
nohup python3 main.py 

# Start ngrok
nohup ngrok start --all

echo "All APIs and Ngrok started."
