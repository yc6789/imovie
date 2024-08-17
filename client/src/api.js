import axios from 'axios';

// Set default configuration for axios
axios.defaults.withCredentials = true;

// Create an axios instance with default settings
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000', // Ensure this URL matches your Flask server
  withCredentials: true, // Ensures cookies (like session cookies) are sent with each request
});


// Export the axios instance
export default api;

// API endpoints as functions for consistency

// User Authentication
export const loginUser = (credentials) => api.post('/users/login', credentials);
export const registerUser = (userData) => api.post('/users/register', userData);
export const logoutUser = () => api.post('/users/logout');

// Movie Data
export const fetchTrendingMovies = () => api.get('/movies/trending');
export const fetchMovieDetails = (movieId) => api.get(`/movies/${movieId}`);

// Favorites
export const addFavorite = (movieId) => api.post('/users/favorites', { movie_id: movieId });
export const removeFavorite = (movieId) => api.delete(`/users/favorites/${movieId}`);
export const fetchFavorites = () => api.get('/users/favorites');

// Ratings & Reviews
export const addRating = (ratingData) => api.post('/users/ratings', ratingData);
export const fetchRatings = () => api.get('/users/ratings');
export const fetchReviews = (movieId) => api.get(`/movies/${movieId}/reviews`);
export const addReview = (reviewData) => api.post('/users/ratings', reviewData);

// Watchlist
export const addToWatchlist = (movieId) => api.post('/users/watchlist', { movie_id: movieId });
export const removeFromWatchlist = (movieId) => api.delete(`/users/watchlist/${movieId}`);
export const fetchWatchlist = () => api.get('/users/watchlist');

// Search
export const fetchMoviesBySearchQuery = (query) => api.get(`/movies/search?query=${query}`);
