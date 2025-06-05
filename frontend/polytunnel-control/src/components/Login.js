import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Add this import
import './Login.css';

const Login = ({ setIsAuthenticated, addAlert }) => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const navigate = useNavigate(); // Add this hook

  const handleChange = (e) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (credentials.username && credentials.password) {
      setIsAuthenticated(true);
      addAlert('Login successful!', 'success');
      navigate('/dashboard'); // Add this navigation
    } else {
      addAlert('Please enter both username and password', 'error');
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
          />
        </div>
        <button type="submit" className="login-btn">Log In</button>
      </form>
    </div>
  );
};

export default Login;