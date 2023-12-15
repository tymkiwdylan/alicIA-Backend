#!/bin/bash

# Function to kill a process running on a given port
kill_port() {
    lsof -i tcp:"$1" | awk 'NR!=1 {print $2}' | xargs kill
}

echo "Stopping Flask APIs..."

# Kill APIs running on their respective ports
kill_port 7000
kill_port 9000
kill_port 5000

echo "Flask APIs stopped."

echo "Stopping Ngrok tunnels..."

# Kill all Ngrok processes
pkill -f ngrok

echo "Ngrok tunnels stopped."
