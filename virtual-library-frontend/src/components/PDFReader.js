import React, { useState, useEffect } from 'react';

const PDFReader = ({ bookId, bookTitle, onClose }) => {
  const [bookmark, setBookmark] = useState(null);

  useEffect(() => {
    const savedProgress = localStorage.getItem(`book_${bookId}_progress`);
    if (savedProgress) {
      setBookmark(JSON.parse(savedProgress));
    }
  }, [bookId]);

  const saveProgress = () => {
    const progress = { 
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem(`book_${bookId}_progress`, JSON.stringify(progress));
    setBookmark(progress);
  };

  return (
    <div className="fixed inset-0 bg-white z-50">
      {/* Simplified Navigation Bar */}
      <div className="bg-gray-800 text-white p-4 flex justify-between items-center">
        <button 
          onClick={onClose}
          className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg font-semibold transition"
        >
          ← Back to Library
        </button>
        
        <div className="flex items-center gap-4">
          <span className="text-lg font-semibold">{bookTitle}</span>
          
          {bookmark && (
            <span className="text-sm text-green-300 bg-green-800 px-2 py-1 rounded">
              📍 Last opened: {new Date(bookmark.timestamp).toLocaleDateString()}
            </span>
          )}
        </div>
        
        <button 
          onClick={saveProgress}
          className="bg-green-500 hover:bg-green-600 px-4 py-2 rounded-lg font-semibold transition"
        >
          💾 Save Progress
        </button>
      </div>

      {/* PDF Viewer Area */}
      <div className="h-full pt-16">
        <iframe 
          src={`http://localhost:5000/books/${encodeURIComponent(bookTitle)}/view`}
          className="w-full h-full"
          title="PDF Viewer"
          onLoad={saveProgress} // Auto-save when PDF loads
        />
      </div>
    </div>
  );
};

export default PDFReader;