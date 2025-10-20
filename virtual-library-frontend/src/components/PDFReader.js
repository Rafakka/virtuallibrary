import React, { useState, useEffect } from 'react';

const PDFReader = ({ bookId, bookTitle, onClose }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [bookmark, setBookmark] = useState(null);

  useEffect(() => {
    const savedProgress = localStorage.getItem(`book_${bookId}_progress`);
    if (savedProgress) {
      setBookmark(JSON.parse(savedProgress));
      setCurrentPage(JSON.parse(savedProgress).page || 1);
    }
  }, [bookId]);

  const saveProgress = (page) => {
    const progress = { page, timestamp: new Date().toISOString() };
    localStorage.setItem(`book_${bookId}_progress`, JSON.stringify(progress));
    setBookmark(progress);
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      saveProgress(newPage);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      saveProgress(newPage);
    }
  };

  return (
    <div className="fixed inset-0 bg-white z-50">
      {/* Navigation Bar */}
      <div className="bg-gray-800 text-white p-4 flex justify-between items-center">
        <button 
          onClick={onClose}
          className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded"
        >
          ← Back to Library
        </button>
        
        <div className="flex items-center gap-4">
          <span className="text-lg font-semibold">{bookTitle}</span>
          <div className="flex items-center gap-2">
            <button onClick={handlePrevPage} disabled={currentPage === 1}>
              ◀
            </button>
            <span>Page {currentPage} of {totalPages}</span>
            <button onClick={handleNextPage} disabled={currentPage === totalPages}>
              ▶
            </button>
          </div>
          
          {bookmark && (
            <span className="text-sm text-green-300">
              📍 Last read: Page {bookmark.page}
            </span>
          )}
        </div>
      </div>

      {/* PDF Viewer Area */}
      <div className="h-full pt-16">
        <iframe 
          src={`http://localhost:5000/books/${encodeURIComponent(bookTitle)}/view`}
          className="w-full h-full"
          title="PDF Viewer"
        />
      </div>
    </div>
  );
};

export default PDFReader;