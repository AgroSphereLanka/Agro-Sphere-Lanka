import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = ({ setIsAuthenticated, addAlert }) => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!credentials.username || !credentials.password) {
      addAlert('Please enter both username and password', 'error');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // This is important for cookies/session
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        setIsAuthenticated(true);
        addAlert('Login successful!', 'success');
        navigate('/dashboard');
      } else {
        const data = await response.json();
        addAlert(data.message || 'Invalid username or password', 'error');
      }
    } catch (error) {
      console.error('Login error:', error);
      addAlert('Failed to connect to server', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Login to Polytunnel Control</h2>
      <form onSubmit={handleLogin}>
        <div className="form-group">
          <label>Username:</label>
          <input 
            type="text" 
            name="username"
            value={credentials.username}
            onChange={handleChange}
            placeholder="Enter username"
            disabled={isLoading}
          />
        </div>
        <div className="form-group">
          <label>Password:</label>
          <input 
            type="password" 
            name="password"
            value={credentials.password}
            onChange={handleChange}
            placeholder="Enter password"
            disabled={isLoading}
          />
        </div>
        <button type="submit" className="login-btn" disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'Log In'}
        </button>
      </form>
    </div>
  );
};

export default Login;