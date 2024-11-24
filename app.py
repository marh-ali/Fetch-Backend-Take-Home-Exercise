from flask import Flask, request, jsonify
import uuid
from points_calculator import calculate_points

app = Flask(__name__)

# In-memory storage for receipts
receipts = {}


@app.route("/receipts/process", methods=["POST"])
def process_receipt():
    try:
        receipt = request.get_json()
        receipt_id = str(uuid.uuid4())
        receipts[receipt_id] = receipt
        return jsonify({"id": receipt_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/receipts/<id>/points", methods=["GET"])
def get_points(id):
    if id not in receipts:
        return jsonify({"error": "Receipt not found"}), 404

    points = calculate_points(receipts[id])
    return jsonify({"points": points}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
