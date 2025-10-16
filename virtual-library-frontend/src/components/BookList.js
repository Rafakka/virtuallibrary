import React, { useState, useEffect } from 'react';
import { getAllBooks, deleteBook, toggleReadStatus, convertBook, getBookFilePath } from '../services/api';
import SearchBar from './SearchBar';

const BookList = () => {
  const [books, setBooks] = useState([]);
  const [displayedBooks, setDisplayedBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  useEffect(() => {
    loadBooks();
  }, []);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const booksData = await getAllBooks();
      setBooks(booksData);
      setDisplayedBooks(booksData);
      setError(null);
    } catch (err) {
      setError('Failed to load books');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReadStatus = async (bookTitle) => {
    try {
      await toggleReadStatus(bookTitle);
      loadBooks();
    } catch (error) {
      console.error('Toggle failed:', error);
    }
  }
  
  const handleOpenInBrowser = async (book) => {
    if (book.extension === '.pdf') {
      window.location.href = `http://localhost:5000/books/${encodeURIComponent(book.title)}/view`;
    } else {
      const shouldConvert = window.confirm('Convert to PDF?');
      if (shouldConvert) {
        try {
          const filePath = await getBookFilePath(book.title);
          await convertBook(filePath);
          window.location.href = `http://localhost:5000/books/${encodeURIComponent(book.title)}/view`;
        } catch (error) {
          alert('Cannot open book: ' + error.message);
        }
      }
    }
  };
  const handleDelete = async (bookTitle) => {
      try {
        await deleteBook(bookTitle);
        loadBooks();
      } catch (error) {
        console.error('Delete failed:', error);
      }
  };
  
  const handleSearchResults = (searchResults) => {
    if (searchResults === null) {
      setDisplayedBooks(books);
      setIsSearching(false);
    } else {
      setDisplayedBooks(searchResults);
      setIsSearching(true);
    }
  };
  if (loading) return <div>Loading books...</div>;
  if (error) return <div>Error: {error}</div>;

   return (
  <div>
    <h2>My Library ({displayedBooks.length} books)</h2>
    
    <SearchBar onSearchResults={handleSearchResults} />
    
    {/* Only show Refresh All when NOT searching */}
    {!isSearching && (
      <button onClick={loadBooks}>Refresh All</button>
    )}
    
    <div className="book-list">
      {displayedBooks.map(book => (
        <div key={book.id} className="book-item">
          <h3>{book.title}</h3>
          <p>Format: {book.extension}</p>
          <p>Status: {book.read ? 'Read' : 'Unread'}</p>
          <button onClick={() => handleDelete(book.title)}>
            Delete
          </button>
          <button onClick={() => handleReadStatus(book.title)}>
            {book.read ? 'Mark as Unread' : 'Mark as Read'}
          </button>
          <button onClick={() => handleOpenInBrowser(book)}>
            Open in Browser
          </button>
        </div>
      ))}
    </div>
  </div>
  );

};

export default BookList;