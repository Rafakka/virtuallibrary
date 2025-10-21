import os
import shutil
import sys
import threading
import webbrowser

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS 
from book_manager import add_converted_book_to_db, cleanup_orphaned_books, does_it_exists, find_pdf_version, get_book_title_by_path, id_pub_file_book, insert_book_if_not_exists, list_books, read_or_not, remove_book, search_books_by_title
from converter import BookConverter
from db import connect_db, init_db
from config_manager import get_books_folder, set_books_folder, load_config

app = Flask(__name__, static_folder='virtual-library-frontend/build', static_url_path='')

init_db()
CORS(app)
config = load_config()

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    react_build_path = os.path.join(base_dir, 'virtual-library-frontend', 'build')
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    react_build_path = os.path.join(base_dir, 'virtual-library-frontend', 'build')

app = Flask(__name__, static_folder=react_build_path, static_url_path='')

def open_browser():
    """Open browser to localhost:5000"""
    import time
    time.sleep(2)
    webbrowser.open("http://localhost:5000")

@app.route('/')
def serve_react():
    return send_file(os.path.join(react_build_path, 'index.html'))

@app.route("/api/")
def home():
    return {"message": "Welcome to the Virtual Library!"}

@app.route("/config/books-folder", methods=["GET"])
def get_books_folder_endpoint():
    current_folder = get_books_folder()
    return jsonify({"books_folder": current_folder})

@app.route("/config/books-folder", methods=["POST"])
def update_books_folder():
    data = request.get_json()
    new_folder = data.get('folder_path')
    
    if not new_folder or not os.path.exists(new_folder):
        return jsonify({"error": "Folder path does not exist"}), 400
    
    try:
        success = set_books_folder(new_folder)
        if success:
            return jsonify({
                "success": True, 
                "message": f"Books folder updated to {new_folder}",
                "books_folder": new_folder
            })
        else:
            return jsonify({"error": "Failed to save configuration"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/booksdb", methods=["POST"])
def update_books():
    data = request.get_json()
    
    if not data or 'folder_path' not in data:
        folder_path = get_books_folder()
    else:
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
            c.execute('SELECT * FROM books WHERE id = ?', (book_id,))
            book = c.fetchone()
            
            if book:
                current_books_folder = get_books_folder()
                deleted_folder = os.path.join(current_books_folder, 'deleted')
                os.makedirs(deleted_folder, exist_ok=True)
                
                original_path = book['path']
                if os.path.exists(original_path):
                    filename = os.path.basename(original_path)
                    new_path = os.path.join(deleted_folder, filename)
                    shutil.move(original_path, new_path)
                    print(f"📁 Moved {filename} to deleted folder")
                
                c.execute('DELETE FROM books WHERE id = ?', (book_id,))
                conn.commit()
                
                return jsonify({"success": True, "message": f"Book moved to deleted folder and won't be scanned again"})
            else:
                return jsonify({"success": False, "message": "Book not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route("/books/convert", methods=["POST"])
def convert_book():
    print("🔄 Conversion endpoint called!")
    data = request.get_json()
    file_path = data.get('file_path')
    print(f"📁 Converting file: {file_path}")

    try:
        full_file_path = file_path

        if not os.path.exists(full_file_path):
            print("❌ File not found")
            return jsonify({"error": "File not found"}), 404
            
        is_epub_file = id_pub_file_book(full_file_path)
        print(f"📖 Is EPUB file: {is_epub_file}")

        if not is_epub_file:
            return jsonify({"error": "File is not an EPUB file"}), 415
        else:
            print("🔄 Starting BookConverter...")
            converter = BookConverter()
            pdf_path = converter.convert_epub_to_pdf(full_file_path)
            print(f"✅ Conversion successful: {pdf_path}")
            
            original_title = get_book_title_by_path(full_file_path)
            print(f"📝 Original title: {original_title}")
            
            add_converted_book_to_db(original_title, pdf_path)
            print("💾 Added to database")
            
            return jsonify({
                "success": "File converted to PDF and added to library.",
                "pdf_path": pdf_path
            }), 201
            
    except Exception as e:
        print(f"❌ Conversion error: {e}")
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
    result = read_or_not(book_id)
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 404

@app.route("/books/<int:book_id>/rename", methods=["PATCH"])
def rename_book(book_id):
    data = request.get_json()
    new_title = data.get('new_title')
    
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('UPDATE books SET title = ? WHERE id = ?', (new_title, book_id))
            conn.commit()
            return jsonify({"success": True, "message": f"Book renamed to {new_title}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/cleanup-orphaned", methods=["POST"])
def cleanup_orphaned():
    count = cleanup_orphaned_books()
    return jsonify({"message": f"Cleaned up {count} orphaned books"})

@app.errorhandler(404)
def not_found(e):
    return send_file('virtual-library-frontend/build/index.html')

if __name__ == '__main__':
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)