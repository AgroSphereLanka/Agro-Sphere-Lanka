import React from 'react';
import './AlertSystem.css';

const AlertSystem = ({ alerts }) => {
  return (
    <div className="alert-container">
      {alerts.map(alert => (
        <div key={alert.id} className={`alert alert-${alert.type}`}>
          {alert.message}
        </div>
      ))}
    </div>
  );
};

export default AlertSystem;