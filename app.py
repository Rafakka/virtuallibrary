import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS 

from book_manager import add_converted_book_to_db, does_it_exists, find_pdf_version, get_book_title_by_path, id_pub_file_book, insert_book_if_not_exists, list_books, read_or_not, remove_book, search_books_by_title
from converter import BookConverter
from db import connect_db, init_db

app = Flask(__name__)
BOOKS_FOLDER = os.path.join(os.path.dirname(__file__), 'bundle test')
init_db()
CORS(app)

@app.route("/")
def home():
    return {"message": "Welcome to the Virtual Library!"}

@app.route("/config/books-folder", methods=["GET"])
def get_books_folder():
    return jsonify({"books_folder": BOOKS_FOLDER})

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
    
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            # Get book info first
            c.execute('SELECT * FROM books WHERE id = ?', (book_id,))
            book = c.fetchone()
            
            if book:
                # Create deleted folder if it doesn't exist
                deleted_folder = os.path.join(BOOKS_FOLDER, 'deleted')
                os.makedirs(deleted_folder, exist_ok=True)
                
                # Move file to deleted folder
                original_path = book['path']
                if os.path.exists(original_path):
                    filename = os.path.basename(original_path)
                    new_path = os.path.join(deleted_folder, filename)
                    shutil.move(original_path, new_path)
                
                # Delete from database
                c.execute('DELETE FROM books WHERE id = ?', (book_id,))
                conn.commit()
                
                return {"success": True, "message": f"Book moved to deleted folder"}
            else:
                return {"success": False, "message": "Book not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route("/books/convert", methods=["POST"])
def convert_book():
    data = request.get_json()
    file_path = data.get('file_path')

    try:
        full_file_path = file_path

        if not os.path.exists(full_file_path):
            return jsonify({"error": "File not found"}), 404
            
        is_epub_file = id_pub_file_book(full_file_path)

        if not is_epub_file:
            return jsonify({"error": "File is not an EPUB file"}), 415
        else:
            converter = BookConverter()
            pdf_path = converter.convert_epub_to_pdf(full_file_path)
            
            original_title = get_book_title_by_path(full_file_path)
            
            add_converted_book_to_db(original_title, pdf_path)
            
            return jsonify({
                "success": "File converted to PDF and added to library.",
                "pdf_path": pdf_path
            }), 201
            
    except Exception as e:
        return jsonify({"error": f"Conversion error: {e}"}), 500

@app.route("/books/<string:title>/view", methods=["GET"])
def view_books(title):
    try:
        original_path = does_it_exists(title)
        if not original_path:
            return jsonify({"error": "Book not found"}), 404
        
        pdf_path = find_pdf_version(original_path)
        if not pdf_path:
            return jsonify({"error": "PDF version not found. Convert EPUB first."}), 404

        return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')
        
    except Exception as e:
        return jsonify({"error": f"Error serving file: {e}"}), 500


@app.route("/books/<int:book_id>/read", methods=["PATCH"])
def toggle_read_status(book_id):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM books WHERE id = ?', (book_id,))
            book = c.fetchone()
            
            if book:
                c.execute('UPDATE books SET read = CASE WHEN read THEN 0 ELSE 1 END WHERE id = ?', (book_id,))
                conn.commit()
                return {"success": True, "message": f"Book read status toggled"}
            else:
                return {"success": False, "message": f"Book not found"}
                
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route("/books/<int:book_id>/rename", methods=["PATCH"])
def rename_book(book_id):
    data = request.get_json()
    new_title = data.get('new_title')
    
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('UPDATE books SET title = ? WHERE id = ?', (new_title, book_id))
            conn.commit()
            return {"success": True, "message": f"Book renamed to {new_title}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)