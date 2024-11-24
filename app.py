from flask import Flask, Request, Response, jsonify, request
import uuid
from points_calculator import calculate_points
from validators import validate_receipt
from typing import Dict

app = Flask(__name__)

# In-memory storage for receipts
receipts: Dict[str, dict] = {}


@app.route("/receipts/process", methods=["POST"])
def process_receipt() -> Response:
    """Process a receipt and return a unique ID.

    Accepts a JSON receipt in the request body and validates its format.
    If valid, stores the receipt and returns a unique identifier.

    Request Body Format:
    {
        "retailer": str,
        "purchaseDate": str (YYYY-MM-DD),
        "purchaseTime": str (HH:MM),
        "items": [
            {
                "shortDescription": str,
                "price": str (XX.XX)
            },
            ...
        ],
        "total": str (XX.XX)
    }

    Returns:
        tuple: (JSON response, HTTP status code)
            Success: ({"id": "<uuid>"}, 200)
            Validation Error: ({"error": "<error message>"}, 400)
            Server Error: ({"error": "Internal server error"}, 500)

    Example:
        >>> # Valid request
        >>> POST /receipts/process
        >>> {
        ...     "retailer": "Target",
        ...     "purchaseDate": "2022-01-01",
        ...     "purchaseTime": "13:01",
        ...     "items": [
        ...         {"shortDescription": "Mountain Dew 12PK", "price": "6.49"}
        ...     ],
        ...     "total": "6.49"
        ... }
        >>> # Response: {"id": "a7e8f9b1-c2d3-4e5f-6g7h-8i9j0k1l2m3n"}
    """
    try:
        receipt = request.get_json()
        validate_receipt(receipt)
        receipt_id = str(uuid.uuid4())
        receipts[receipt_id] = receipt
        return jsonify({"id": receipt_id}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@app.route("/receipts/<id>/points", methods=["GET"])
def get_points(id: str) -> Response:
    """Calculate and return points for a processed receipt.

    Retrieves a receipt by ID and calculates its points based on the rules:
    1. One point for every alphanumeric character in the retailer name
    2. 50 points if the total is a round dollar amount with no cents
    3. 25 points if the total is a multiple of 0.25
    4. 5 points for every two items on the receipt
    5. Points for item descriptions with length multiple of 3
    6. 6 points if the day in the purchase date is odd
    7. 10 points if the time of purchase is between 2:00pm and 4:00pm

    Args:
        id: The UUID of the receipt to calculate points for

    Returns:
        tuple: (JSON response, HTTP status code)
            Success: ({"points": <int>}, 200)
            Not Found: ({"error": "Receipt not found"}, 404)

    Example:
        >>> # Valid request
        >>> GET /receipts/a7e8f9b1-c2d3-4e5f-6g7h-8i9j0k1l2m3n/points
        >>> # Response: {"points": 32}
    """
    if id not in receipts:
        return jsonify({"error": "Receipt not found"}), 404

    points = calculate_points(receipts[id])
    return jsonify({"points": points}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
