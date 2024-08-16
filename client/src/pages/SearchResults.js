import React, { useState, useEffect } from 'react';
import axios from '../api';
import MovieCard from '../components/MovieCard';

const SearchResults = ({ query }) => {
    const [movies, setMovies] = useState([]);

    useEffect(() => {
        axios.get(`/movies/search?query=${query}`)
            .then(response => setMovies(response.data))
            .catch(error => console.error('Error fetching search results:', error));
    }, [query]);

    return (
        <div className="container">
            <h2 className="my-4">Search Results</h2>
            <div className="row">
                {movies.map(movie => (
                    <MovieCard key={movie.id} movie={movie} />
                ))}
            </div>
        </div>
    );
};

export default SearchResults;
