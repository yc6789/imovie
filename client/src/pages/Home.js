import React, { useContext, useEffect, useState } from 'react';
import { UserContext } from '../UserContext';
import { fetchTrendingMovies } from '../api';
import MovieCard from '../components/MovieCard';
import bannerImage from '../banner.png';

const Home = () => {
  const { user } = useContext(UserContext);
  const [trendingMovies, setTrendingMovies] = useState([]);

  useEffect(() => {
    fetchTrendingMovies()
      .then(response => setTrendingMovies(response.data))
      .catch(error => console.error('Error fetching trending movies:', error));
  }, []);

  return (
    <div>
      <div className="hero-section" style={{ backgroundImage: `url(${bannerImage})` }}>
        <div className="hero-content text-center text-white">
          <h1>Welcome to iMovie</h1>
          <p>Discover the best movies, just for you</p>
        </div>
      </div>

      <div className="container mt-4">
        <h2 className="text-center">Trending Movies</h2>
        <div className="row">
          {trendingMovies.map(movie => (
            <div className="col-md-3 mb-4" key={movie.id}>
              <MovieCard movie={movie} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Home;
