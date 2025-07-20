from flask import Flask, jsonify, request
from .external_api import fetch_product_by_barcode, fetch_product_by_name

# In‑memory store
inventory = []
next_id = 1


def create_app():
    app = Flask(__name__)

    @app.route('/inventory', methods=['GET'])
    def get_all_items():
        # return the full list
        return jsonify(inventory), 200

    @app.route('/inventory/<int:item_id>', methods=['GET'])
    def get_item(item_id):
        item = next((i for i in inventory if i['id'] == item_id), None)
        if item is None:
            return jsonify({'message': 'Item not found'}), 404
        return jsonify(item), 200

    @app.route('/inventory', methods=['POST'])
    def add_item():
        global next_id
        data = request.get_json() or {}
        name = data.get('name')
        if not name:
            return jsonify({'message': 'Name is required'}), 400

        item = {
            'id': next_id,
            'name': name,
            'quantity': data.get('quantity', 0),
            'details': data.get('details', {})
        }
        inventory.append(item)
        next_id += 1
        return jsonify(item), 201

    @app.route('/inventory/<int:item_id>', methods=['PATCH'])
    def update_item(item_id):
        data = request.get_json() or {}
        item = next((i for i in inventory if i['id'] == item_id), None)
        if item is None:
            return jsonify({'message': 'Item not found'}), 404

        # patch only allowed fields
        for key in ('name', 'quantity', 'details'):
            if key in data:
                item[key] = data[key]
        return jsonify(item), 200

    @app.route('/inventory/<int:item_id>', methods=['DELETE'])
    def delete_item(item_id):
        global inventory
        if not any(i['id'] == item_id for i in inventory):
            return jsonify({'message': 'Item not found'}), 404
        inventory = [i for i in inventory if i['id'] != item_id]
        return '', 204

    @app.route('/inventory/fetch', methods=['GET'])
    def fetch_external():
        barcode = request.args.get('barcode')
        name = request.args.get('name')

        if not barcode and not name:
            return jsonify({'message': 'barcode or name query required'}), 400

        if barcode:
            product = fetch_product_by_barcode(barcode)
        else:
            product = fetch_product_by_name(name)

        if not product:
            return jsonify({'message': 'Product not found in external API'}), 404

        return jsonify(product), 200

    return app
