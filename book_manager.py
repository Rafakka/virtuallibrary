import os
from pathlib import Path
import platform
import webbrowser
import filetype

from converter import BookConverter
from db import connect_db

def list_books(folder_path):
    supported_extensions = ['.pdf', '.epub', '.mobi']
    found_books = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_extensions:
                full_path = os.path.join(root, file)
                found_books.append({
                    'title': os.path.splitext(file)[0],
                    'extension': ext,
                    'path': full_path
                })
    return found_books

def insert_book_if_not_exists(books):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            books_added = 0
            
            for book in books:
                c.execute('SELECT id FROM books WHERE path = ?', (book['path'],))
                result = c.fetchone()
                if result is None:
                    c.execute(
                        'INSERT INTO books(title, extension, path) VALUES (?,?,?)',
                        (book['title'], book['extension'], book['path'])
                    )
                    books_added += 1
                    print(f"Added {book['title']}")
                else:
                    print(f"Already in the database: {book['title']}")

            return {"success": True, "books_added": books_added}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_books_by_title(title_query):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT * FROM books 
                WHERE LOWER(title) LIKE LOWER(?)
                ORDER BY title
            ''', (f'%{title_query}%',))
            books = c.fetchall()
            return [dict(book) for book in books]
    except Exception as e:
        return {"success": False, "error": str(e)}
    
def add_converted_book_to_db(original_title, pdf_path):
    """Add converted PDF to database"""
    try:
        with connect_db() as conn:
            c = conn.cursor()
            
            # Check if PDF already exists in database
            c.execute('SELECT id FROM books WHERE path = ?', (pdf_path,))
            if c.fetchone():
                print(f"PDF already in database: {pdf_path}")
                return
            
            # Add PDF version to database
            c.execute('''
                INSERT INTO books (title, extension, path) 
                VALUES (?, ?, ?)
            ''', (original_title, '.pdf', pdf_path))
            conn.commit()
            print(f"✅ Added converted PDF to database: {pdf_path}")
            
    except Exception as e:
        print(f"❌ Error adding converted PDF to database: {e}")
        raise

def read_or_not(title):
    try:
            with connect_db() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM books WHERE title = ?', (title,))
                book = c.fetchone()
                
                if book: 

                    c.execute('UPDATE books SET read = CASE WHEN read = 1 THEN 0 ELSE 1 END WHERE title = ?', (title,))

                    return {"success": True, "message": f"Book '{title}' read"}
                else:
                    return {"success": False, "message": f"Book '{title}' not found"}
                    
    except Exception as e:
            return {"success": False, "error": str(e)}


def remove_book(title):
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM books WHERE title = ?', (title,))
            book = c.fetchone()
            
            if book:
                c.execute('DELETE FROM books WHERE title = ?', (title,))

                return {"success": True, "message": f"Book '{title}' deleted"}
            else:
                return {"success": False, "message": f"Book '{title}' not found"}
                
    except Exception as e:
        return {"success": False, "error": str(e)}

def id_pub_file_book(file_path):
    print(f"🔍 Checking EPUB for: {file_path}")  # Debug
    
    if not os.path.exists(file_path):
        print("❌ File doesn't exist")
        return False
    
    try:
        # Check file extension first
        file_extension = Path(file_path).suffix.lower()
        print(f"📄 File extension: {file_extension}")  # Debug
        
        if file_extension == '.epub':
            print("✅ Valid EPUB by extension")
            return True
            
        # kind = filetype.guess(file_path)
        # print(f"File type detection: {kind}")
            
        return False
    except Exception as e:
        print(f"❌ Error checking file type: {e}")
        return False
    
def id_pdf_file_book(file_path):
    if not os.path.exists(file_path):
        return False
    
    try:
        kind = filetype.guess(file_path)
        if kind and kind.extension == 'pdf':
            return True
        
        file_extension = Path(file_path).suffix.lower()
        if file_extension == '.pdf':
            return True
            
        return False
    except Exception as e:
        print(f"Error checking file type: {e}")
        return False

def does_it_exists(title):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM books WHERE title = ?", (title,))
            result = cursor.fetchone()
            
            if result:
                return result[0] 
            else:
                return None

    except Exception as e:
        print(f"Database error: {e}") 
        return None

def find_pdf_version(original_path):
    
    if id_pdf_file_book(original_path):
        return original_path
    
    converted_path = get_converted_pdf_path(original_path)
    if os.path.exists(converted_path):
        return converted_path
    
    return None

def get_converted_pdf_path(original_path):
    """Get path of converted PDF"""
    base = os.path.splitext(original_path)[0]
    return base + '_converted.pdf'
    
def find_pdf_version(original_path):

    if original_path.lower().endswith('.pdf'):
        return original_path
    
    base = os.path.splitext(original_path)[0]
    converted_path = base + '_converted.pdf'
    
    if os.path.exists(converted_path):
        return converted_path
    
    return None

def get_book_title_by_path(file_path):
    """Get book title from database using file path"""
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('SELECT title FROM books WHERE path = ?', (file_path,))
            result = c.fetchone()
            if result:
                return result[0]
            else:
                raise Exception("Book not found in database")
    except Exception as e:
        print(f"Error getting book title: {e}")
        raise