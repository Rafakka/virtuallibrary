import React, { useState, useEffect } from 'react';
import { getBooksFolder, updateBooksFolder } from '../services/api';

const Settings = ({ onClose }) => {
  const [booksFolder, setBooksFolder] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadCurrentFolder();
  }, []);

  const loadCurrentFolder = async () => {
    try {
      const folder = await getBooksFolder();
      setBooksFolder(folder);
    } catch (error) {
      setMessage('Error loading current folder');
    }
  };

  const handleSave = async () => {
    if (!booksFolder.trim()) {
      setMessage('Please enter a folder path');
      return;
    }

    try {
      setLoading(true);
      setMessage('');
      await updateBooksFolder(booksFolder);
      setMessage('✅ Folder location updated successfully!');
      setTimeout(() => onClose(), 1500); // Close after success
    } catch (error) {
      setMessage('❌ Error updating folder: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBrowse = () => {
    // Note: Browser security limits file input to specific use cases
    // This is a simple text input approach
    const newPath = prompt('Enter the full path to your books folder:', booksFolder);
    if (newPath) {
      setBooksFolder(newPath);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-4">📁 Library Settings</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Books Folder Location
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={booksFolder}
              onChange={(e) => setBooksFolder(e.target.value)}
              placeholder="/path/to/your/books"
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleBrowse}
              className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded-lg"
            >
              Browse
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Enter the full path to your books folder
          </p>
        </div>

        {message && (
          <div className={`p-3 rounded-lg mb-4 ${
            message.includes('✅') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message}
          </div>
        )}

        <div className="flex gap-2 justify-end">
          <button
            onClick={onClose}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;