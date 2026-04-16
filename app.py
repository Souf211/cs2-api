from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from config import Config
from models import db, Item

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

db.init_app(app)

logging.basicConfig(
    filename=app.config["LOG_FILE"],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "API is running",
        "endpoints": {
            "GET /items": "Get all items",
            "GET /items/<id>": "Get one item",
            "POST /items": "Create item",
            "PUT /items/<id>": "Update item",
            "DELETE /items/<id>": "Delete item"
        }
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/items", methods=["GET"])
def get_items():
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items]), 200

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item.to_dict()), 200

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    name = data.get("name")
    description = data.get("description", "")
    price = data.get("price", 0)

    if not name:
        return jsonify({"error": "Name is required"}), 400

    try:
        price = float(price)
    except (ValueError, TypeError):
        return jsonify({"error": "Price must be a number"}), 400

    new_item = Item(name=name, description=description, price=price)
    db.session.add(new_item)
    db.session.commit()

    logging.info(f"Created item with id {new_item.id}")

    return jsonify({
        "message": "Item created successfully",
        "item": new_item.to_dict()
    }), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    if "name" in data:
        if not data["name"]:
            return jsonify({"error": "Name cannot be empty"}), 400
        item.name = data["name"]

    if "description" in data:
        item.description = data["description"]

    if "price" in data:
        try:
            item.price = float(data["price"])
        except (ValueError, TypeError):
            return jsonify({"error": "Price must be a number"}), 400

    db.session.commit()

    logging.info(f"Updated item with id {item.id}")

    return jsonify({
        "message": "Item updated successfully",
        "item": item.to_dict()
    }), 200

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    logging.info(f"Deleted item with id {item.id}")

    return jsonify({"message": "Item deleted successfully"}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8000, debug=True)