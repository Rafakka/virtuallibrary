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

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading your library...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
        <div className="text-red-500 text-2xl mb-2">⚠️</div>
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Books</h3>
        <p className="text-red-600">{error}</p>
        <button 
          onClick={loadBooks}
          className="mt-4 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
        >
          Try Again
        </button>
      </div>
    </div>
  );

  return (
  <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">📚 My Virtual Library</h1>
        <p className="text-gray-600 text-lg">{displayedBooks.length} books in your collection</p>
      </div>

      {/* Search & Controls */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="flex-1 w-full">
            <SearchBar onSearchResults={handleSearchResults} />
          </div>
          {!isSearching && (
            <button 
              onClick={loadBooks}
              className="bg-indigo-500 hover:bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 hover:scale-105"
            >
              🔄 Refresh Library
            </button>
          )}
        </div>
      </div>

      {/* Books Grid */}
      {displayedBooks.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📖</div>
          <h3 className="text-2xl font-semibold text-gray-700">No books found</h3>
          <p className="text-gray-500">Try a different search or refresh your library</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {displayedBooks.map(book => (
            <div key={book.id} className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
              {/* Book Card */}
              <div className="p-6">
                {/* Title */}
                <h3 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">{book.title}</h3>
                
                {/* Metadata */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="bg-gray-100 px-2 py-1 rounded">📄 {book.extension}</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <span className={`px-2 py-1 rounded-full ${book.read ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {book.read ? '✅ Read' : '📖 Unread'}
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-2">
                  <button 
                    onClick={() => handleOpenInBrowser(book)}
                    className="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium transition"
                  >
                    👁️ Open
                  </button>
                  <button 
                    onClick={() => handleReadStatus(book.title)}
                    className="flex-1 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded-lg text-sm font-medium transition"
                  >
                    {book.read ? '↶ Unread' : '✓ Read'}
                  </button>
                  <button 
                    onClick={() => handleDelete(book.title)}
                    className="flex-1 bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded-lg text-sm font-medium transition"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  </div>
  );
}

export default BookList;