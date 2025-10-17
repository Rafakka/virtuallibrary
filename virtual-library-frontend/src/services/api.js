import axios from 'axios';

const API_BASE = 'http://localhost:5000';
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const getBooksFolder = async () => {
  try {
    const response = await api.get('/config/books-folder');
    return response.data.books_folder;
  } catch (error) {
    console.error('Error getting books folder:', error);
    throw error;
  }
};


// GET all books
export const getAllBooks = async () => {
  try {
    const response = await api.get('/books');
    return response.data;
  } catch (error) {
    console.error('Error fetching books:', error);
    throw error;
  }
};

// POST - Sync books from folder
export const syncBooks = async (folderPath) => {
  const response = await api.post('/booksdb', { folder_path: folderPath });
  return response.data;
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
export const toggleReadStatus = async (bookId) => {
  const response = await api.patch(`/books/${bookId}/read`);
  return response.data;
};

// DELETE - Remove book
export const deleteBook = async (bookId) => {
  try {
    const response = await api.delete(`/books/${bookId}`);
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
