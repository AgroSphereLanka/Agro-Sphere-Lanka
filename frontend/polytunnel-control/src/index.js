import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Initialize localStorage if needed
if (!localStorage.getItem('isAuthenticated')) {
  localStorage.setItem('isAuthenticated', 'false');
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);