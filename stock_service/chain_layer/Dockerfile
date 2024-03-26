# Use an official lightweight Python image
# Python 3.11 is used here as an example
FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY src/ .

# Specify the port the app runs on
EXPOSE 7000

# Command to run the application
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:7000", "--workers", "3", "--timeout", "1000"]
