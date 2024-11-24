# Receipt Processor

A Flask-based web service that processes receipts and awards points based on specific rules. This service provides two endpoints:

- Process receipts and generate unique IDs
- Calculate points for processed receipts based on defined rules

## Prerequisites

- Docker

## Quick Start

1. Build the Docker image:

```bash
docker build -t receipt-processor .
```

2. Run the Docker container:

```bash
docker run --name receipt-processor-ali-marhoon -p 8080:8080 receipt-processor
```

The service will be available at `http://<host>:8080`.

## API Endpoints

### 1.Process Receipts

- **Endpoint:** `/receipts/process`
- **Method:** POST
- **Content-Type:** application/json
- **Request Body Example:**

```json
{
  "retailer": "Target",
  "purchaseDate": "2022-01-01",
  "purchaseTime": "13:01",
  "items": [
    {
      "shortDescription": "Mountain Dew 12PK",
      "price": "6.49"
    }
  ],
  "total": "6.49"
}
```

- **Success Response:**

```json
{
  "id": "a7e8f9b1-c2d3-4e5f-6g7h-8i9j0k1l2m3n"
}
```

### 2. Get Points for a Receipt

- **Endpoint:** `/receipts/{id}/points`
- **Method:** GET
- **Success Response:**

```json
{
  "points": 12
}
```

## Points Calculation Rules

Points are awarded based on the following rules:

1. One point for every alphanumeric character in the retailer name
2. 50 points if the total is a round dollar amount with no cents
3. 25 points if the total is a multiple of 0.25
4. 5 points for every two items on the receipt
5. If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer
6. 6 points if the day in the purchase date is odd
7. 10 points if the time of purchase is between 2:00pm and 4:00pm

## Project Structure

├── app.py # Main application file with API endpoints

├── points_calculator.py # Points calculation logic

├── validators.py # Input validation

├── tests/ # Test files

├── requirements.txt # Python dependencies

└── Dockerfile # Docker configuration

## Running Tests

Tests can be run inside the Docker container:

```bash
docker run receipt-processor pytest
```

## Implementation Notes

- Data is stored in memory and does not persist between application restarts
- The service runs on port 8080 by default
- Input validation ensures all required fields are present and properly formatted
- Error handling provides clear feedback for invalid requests
