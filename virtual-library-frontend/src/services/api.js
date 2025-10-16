import axios from 'axios';

const API_BASE = 'http://localhost:5000';
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// GET all books
export const getAllBooks = async () => {
  try {
    const response = await api.get('/books');
    return response.data;  // Returns the array of books
  } catch (error) {
    console.error('Error fetching books:', error);
    throw error;  // Re-throw so components can handle it
  }
};

// POST - Sync books from folder
export const syncBooks = async (folderPath) => {
  try {
    const response = await api.post('/booksdb', {
      folder_path: folderPath
    });
    return response.data;  // Returns { message, books_added, total_books_found }
  } catch (error) {
    console.error('Error syncing books:', error);
    throw error;
  }
};

// GET - Search books by title
export const searchBooks = async (title) => {
  try {
    const response = await api.get(`/books/${encodeURIComponent(title)}`);
    return response.data;
  } catch (error) {
    console.error('Error searching books:', error);
    throw error;
  }
};


export const convertBook = async (filePath) => {
  const response = await api.post('/books/convert', { file_path: filePath });
  console.log('File path:', filePath);
  return response.data;
};

// PATCH - Toggle read status
export const toggleReadStatus = async (title) => {
  try {
    const response = await api.patch(`/books/${encodeURIComponent(title)}`);
    return response.data;
  } catch (error) {
    console.error('Error toggling read status:', error);
    throw error;
  }
};

// DELETE - Remove book
export const deleteBook = async (title) => {
  try {
    const response = await api.delete(`/books/${encodeURIComponent(title)}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting book:', error);
    throw error;
  }
};

export const getBookFilePath = async (title) => {
  try {
    const response = await api.get(`/books/${encodeURIComponent(title)}`);
    if (response.data.books && response.data.books.length > 0) {
      return response.data.books[0].path;
    }
    throw new Error('Book not found');
  } catch (error) {
    console.error('Error getting book file path:', error);
    throw error;
  }
};
