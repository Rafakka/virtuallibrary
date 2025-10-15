import React, { useState } from 'react';
import { searchBooks } from '../services/api';

const SearchBar = ({ onSearchResults }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      // If empty search, show all books (we'll implement this)
      return;
    }
    
    try {
      const results = await searchBooks(searchTerm);
      onSearchResults(results.books); // Pass results to parent
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleClear = () => {
    setSearchTerm('');
    onSearchResults(null); // Clear results (show all books)
  };

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search books by title..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
      />
      <button onClick={handleSearch}>Search</button>
      <button onClick={handleClear}>Clear</button>
    </div>
  );
};

export default SearchBar;