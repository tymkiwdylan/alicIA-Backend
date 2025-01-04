# Inventory Management System

A microservices-based inventory management system with AI-powered assistance capabilities.

## Overview

This system consists of multiple services that work together to provide a complete inventory management solution:

- **Stock Service**: Handles inventory management, stock levels, and item tracking
- **Customer Service**: Manages customer interactions and communications
- **Auth Service**: Handles authentication and authorization
- **AI Assistant**: Provides intelligent assistance for inventory management tasks

## Features

- Inventory tracking and management
- Stock movement logging
- Price management
- Supplier management
- Batch processing
- Stock valuation
- AI-powered assistance for inventory queries
- Authentication and authorization
- Customer interaction management

## Architecture

The system is built using a microservices architecture with the following components:

- Flask-based REST APIs
- MongoDB for data storage
- OpenAI integration for AI capabilities
- Nginx as reverse proxy
- Docker containerization

## API Documentation

The system provides comprehensive REST APIs for inventory management. Key endpoints include:

- `/search`: Search for inventory items
- `/overview`: Get inventory overview
- `/price`: Manage item prices
- `/movement-log`: Track stock movements
- `/stock-valuation`: Get stock valuations
- `/batch`: Manage item batches
- `/supplier`: Manage suppliers
- `/stock`: Manage stock levels

For complete API documentation, refer to the OpenAPI specification in the `openapi.json` file.

## Setup Requirements

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- MongoDB
- OpenAI API access


### Production Mode

Use Docker Compose to run all services:

```bash
docker compose up -d
```
## Documentation

- API Documentation: Available via OpenAPI specification
- System Architecture: Check the docs folder
- User Guide: Available in the docs folder