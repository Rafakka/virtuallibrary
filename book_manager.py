import os
import sqlite3

from flask import jsonify

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