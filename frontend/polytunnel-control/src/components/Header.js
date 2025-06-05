import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Header.css';

const Header = ({ setIsAuthenticated }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    setIsAuthenticated(false);
    navigate('/login');
  };

  return (
    <header className="app-header">
      <h1>Polytunnel Control System</h1>
      <nav>
        <button onClick={handleLogout}>Logout</button>
      </nav>
    </header>
  );
};

export default Header;