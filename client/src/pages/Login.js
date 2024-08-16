// login.js
import React, { useState, useContext } from 'react';
import { loginUser } from '../api';
import { useNavigate } from 'react-router-dom';
import { UserContext } from '../UserContext';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const { setUser } = useContext(UserContext);

    const handleSubmit = (e) => {
        e.preventDefault();
        loginUser({ username, password })
            .then(response => {
                console.log('API Response:', response);
                if (response.data) {
                    setUser(response.data);
                    localStorage.setItem('user', JSON.stringify(response.data));
                    navigate('/home');
                } else {
                    setError('Login failed: Invalid response');
                    console.error('Error: Invalid user data returned');
                }
            })
            .catch(error => {
                setError('Invalid username or password');
                console.error('Error logging in:', error);
            });
    };

    return (
        <div className="login-page">
            <h2>Login</h2>
            {error && <p className="error">{error}</p>}
            <form onSubmit={handleSubmit}>
                <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
                <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                <button type="submit">Login</button>
            </form>
        </div>
    );
};

export default Login;
