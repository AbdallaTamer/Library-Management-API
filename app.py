from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import json

app = Flask(__name__)
DATA_FILE = 'books.json'

SWAGGER_URL = '/api-docs'
API_URL = '/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Library Management API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

def load_books():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_books(books):
    with open(DATA_FILE, 'w') as file:
        json.dump(books, file, indent=4)

@app.route('/swagger.yaml')
def serve_swagger_yaml():
    return send_from_directory('.', 'swagger.yaml')

@app.route('/books', methods=['POST'])
def add_book():
    book = request.json
    if not all(key in book for key in ('title', 'author', 'published_year', 'isbn')):
        return jsonify({'error': 'Missing required fields'}), 400
    books = load_books()
    books.append(book)
    save_books(books)
    return jsonify(book), 201

@app.route('/books', methods=['GET'])
def list_books():
    return jsonify(load_books())

@app.route('/books/search', methods=['GET'])
def search_books():
    filters = request.args
    books = load_books()
    filtered_books = [book for book in books if all(
        str(book.get(key)).lower() == filters[key].lower() for key in filters)]
    return jsonify(filtered_books)

@app.route('/books/<string:isbn>', methods=['DELETE'])
def delete_book(isbn):
    books = load_books()
    books = [book for book in books if book['isbn'] != isbn]
    save_books(books)
    return '', 204

@app.route('/books/<string:isbn>', methods=['PUT'])
def update_book(isbn):
    books = load_books()
    book = next((b for b in books if b['isbn'] == isbn), None)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    for key, value in request.json.items():
        if key in book:
            book[key] = value
    save_books(books)
    return jsonify(book)

@app.route('/')
def home():
    return "Library Management API is running! Visit /api-docs for API documentation."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)