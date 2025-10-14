import  sqlite3
from contextlib import contextmanager


def init_db():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            extension TEXT NOT NULL,
            read BOOLEAN FALSE,
            path TEXT UNIQUE NOT NULL,
            added_at TIMESTAMP DEFAULT
    CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@contextmanager
def connect_db():
    conn = None
    try:
        conn = sqlite3.connect('books.db')
        conn.row_factory = sqlite3.Row 
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()