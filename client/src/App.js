import React, { useContext } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useNavigate } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import SearchResults from './pages/SearchResults';
import MovieDetails from './pages/MovieDetails';
import { UserContext } from './UserContext';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const { user, setUser } = useContext(UserContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    navigate('/home');
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
            </ul>
            {user ? (
              <button className="btn btn-outline-danger" onClick={handleLogout}>Logout</button>
            ) : (
              <>
                <Link className="btn btn-outline-primary mr-2" to="/login">Login</Link>
                <Link className="btn btn-outline-secondary" to="/register">Register</Link>
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
        </Routes>
      </div>
      <footer className="bg-light text-center py-3">
        <p>&copy; 2024 iMovie. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
