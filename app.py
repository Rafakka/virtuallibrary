import os
from flask import Flask, jsonify, request
from flask_cors import CORS 

from book_manager import id_pub_file_book, insert_book_if_not_exists, list_books, read_or_not, remove_book, search_books_by_title
from converter import BookConverter
from db import connect_db, init_db

app = Flask(__name__)
BOOKS_FOLDER = os.path.join(os.path.dirname(__file__), 'bundle test')
init_db()
CORS(app)

@app.route("/")
def home():
    return {"message": "Welcome to the Virtual Library!"}

@app.route("/booksdb", methods=["POST"])
def update_books():
    data = request.get_json()
    
    if not data or 'folder_path' not in data:
        return jsonify({'error': 'folder_path is required'}), 400
    
    folder_path = data.get("folder_path")
    
    if not os.path.exists(folder_path):
        return jsonify({'error': 'Folder path does not exist'}), 400

    try:
        books = list_books(folder_path)
        result = insert_book_if_not_exists(books)

        if result["success"]:
            return jsonify({
                "message": f"Added {result['books_added']} books to Database.",
                "total_books_found": len(books),
                "books_added": result['books_added']
            })
        else:
            return jsonify({"error": result["error"]}), 500
            
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

@app.route("/books", methods=["GET"])
def get_books():
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM books ORDER BY added_at DESC')
            books = c.fetchall()
            books_list = [dict(book) for book in books]
            return jsonify(books_list)
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500


@app.route("/books/<string:title>", methods=["GET"])
def get_book_by_name(title): 
    try:
        result = search_books_by_title(title)
        
        if isinstance(result, list):
            return jsonify({
                "books": result,
                "count": len(result)
            })
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    
@app.route("/books/<string:title>", methods=["PATCH"])
def update_book(title):
    try:
        result = read_or_not(title)
        if result["success"]:
            return jsonify({"message": result["message"]})
        else:
            return jsonify({"error": result["message"]}), 404

    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route("/books/<string:title>", methods=["DELETE"])
def delete_book(title):
    try:
        result = remove_book(title)
        
        if result["success"]:
            return jsonify({"message": result["message"]})
        else:
            return jsonify({"error": result["message"]}), 404
            
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route("/books/<file_path>/convert", methods=["POST"])
def check_file_first(file_path):
    try:
        full_file_path = os.path.join(BOOKS_FOLDER, file_path)

        if not os.path.exists(full_file_path):
            return jsonify({"error": "File not found"}), 404
            
        is_epub_file = id_pub_file_book(full_file_path)

        if not is_epub_file:
            return jsonify({"error": "File is not an EPUB file, cannot be converted."}), 415
        else:
            converter = BookConverter(BOOKS_FOLDER)
            pdf_path = converter.convert_epub_to_pdf(full_file_path)
            
            return jsonify({
                "success": "File converted to PDF.",
                "pdf_path": os.path.basename(pdf_path)
            }), 201
            
    except Exception as e:
        return jsonify({"error": f"Conversion error: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)