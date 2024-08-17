import React, { useContext, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useNavigate } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import SearchResults from './pages/SearchResults';
import MovieDetails from './pages/MovieDetails';
import { UserContext } from './UserContext';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import MyWatchlist from './pages/MyWatchlist';
import MyFavorites from './pages/MyFavorites';

function App() {
  const { user, setUser } = useContext(UserContext);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    navigate('/home');
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?query=${searchQuery.trim()}`);
      setSearchQuery('');
    }
  };

  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <div className="container">
          <Link className="navbar-brand" to="/home">iMovie</Link>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav mr-auto">
              <li className="nav-item">
                <Link className="nav-link" to="/home">Home</Link>
              </li>
              {user && (
                <>
                  <li className="nav-item">
                    <Link className="nav-link" to="/my-watchlist">My Watchlist</Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to="/my-favorites">My Favorites</Link>
                  </li>
                </>
              )}
            </ul>
            <form className="form-inline my-2 my-lg-0" onSubmit={handleSearchSubmit}>
              <input
                className="form-control mr-sm-2"
                type="search"
                placeholder="Search movies..."
                aria-label="Search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button className="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
            </form>
            {user ? (
              <button className="btn btn-outline-danger ml-2" onClick={handleLogout}>Logout</button>
            ) : (
              <>
                <Link className="btn btn-outline-primary ml-2" to="/login">Login</Link>
                <Link className="btn btn-outline-secondary ml-2" to="/register">Register</Link>
              </>
            )}
          </div>
        </div>
      </nav>
      <div className="container mt-4">
        <Routes>
          <Route path="/home" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="/movies/:id" element={<MovieDetails />} />
          <Route path="/my-watchlist" element={<MyWatchlist />} />
          <Route path="/my-favorites" element={<MyFavorites />} />
        </Routes>
      </div>
      <footer className="bg-light text-center py-3">
        <p>&copy; 2024 iMovie. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
