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
    return response.data;  // Returns { books: [], count: number }
  } catch (error) {
    console.error('Error searching books:', error);
    throw error;
  }
};

// PATCH - Toggle read status
export const toggleReadStatus = async (title) => {
  try {
    const response = await api.patch(`/books/${encodeURIComponent(title)}`);
    return response.data;  // Returns { message: "Book 'title' marked as read" }
  } catch (error) {
    console.error('Error toggling read status:', error);
    throw error;
  }
};

// DELETE - Remove book
export const deleteBook = async (title) => {
  try {
    const response = await api.delete(`/books/${encodeURIComponent(title)}`);
    return response.data;  // Returns { message: "Book 'title' deleted" }
  } catch (error) {
    console.error('Error deleting book:', error);
    throw error;
  }
};