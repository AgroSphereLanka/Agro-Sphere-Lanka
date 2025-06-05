import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import Signup from './components/Signup';
import AlertSystem from './components/AlertSystem';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // Check if user was previously authenticated
    return localStorage.getItem('isAuthenticated') === 'true';
  });
  const [alerts, setAlerts] = useState([]);

  // Persist authentication state
  useEffect(() => {
    localStorage.setItem('isAuthenticated', isAuthenticated);
  }, [isAuthenticated]);

  const addAlert = (message, type = 'info') => {
    const newAlert = { id: Date.now(), message, type };
    setAlerts(prev => [...prev, newAlert]);
    setTimeout(() => {
      setAlerts(prev => prev.filter(alert => alert.id !== newAlert.id));
    }, 5000);
  };

  return (
    <Router>
      <div className="app-container">
        <AlertSystem alerts={alerts} />
        <Routes>
          <Route path="/login" element={
            !isAuthenticated ? 
            <Login 
              setIsAuthenticated={setIsAuthenticated} 
              addAlert={addAlert}
            /> : 
            <Navigate to="/dashboard" />
          } />
          <Route path="/signup" element={
            !isAuthenticated ? 
            <Signup addAlert={addAlert} /> : 
            <Navigate to="/dashboard" />
          } />
          <Route path="/dashboard" element={
            isAuthenticated ? 
            <Dashboard addAlert={addAlert} /> : 
            <Navigate to="/login" />
          } />
          <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;