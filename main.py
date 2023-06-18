from flask import Flask, jsonify
import os
from crud import Crud

app = Flask(__name__)


@app.route('/api/register', methods=['GET'])
def index():
    handler = Crud('user')
    handler.insert(['name'], ['Dani'])

    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
