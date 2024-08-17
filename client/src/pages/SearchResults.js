import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';  // Added Link import
import { fetchMoviesBySearchQuery } from '../api';
import MovieCard from '../components/MovieCard';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

const SearchResults = () => {
  const query = useQuery().get('query');
  const [movies, setMovies] = useState([]);

  useEffect(() => {
    if (query) {
      fetchMoviesBySearchQuery(query)
        .then(response => setMovies(response.data))
        .catch(error => console.error('Error fetching search results:', error));
    }
  }, [query]);

  return (
    <div className="container">
      <h2 className="my-4">Search Results for "{query}"</h2>
      <div className="row">
        {movies.length > 0 ? (
          movies.map(movie => (
            <div className="col-md-3 mb-4" key={movie.id}>
              <MovieCard movie={movie} />
            </div>
          ))
        ) : (
          <div className="col-12 text-center">
            <p>No results found for "{query}". Try searching with different keywords.</p>
            <Link to="/home" className="btn btn-primary">Explore Trending Movies</Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchResults;
