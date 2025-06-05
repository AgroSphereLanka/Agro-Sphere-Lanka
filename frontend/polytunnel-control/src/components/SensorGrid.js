// src/components/SensorGrid.js
import React from 'react';
import { 
  GiWaterDrop, 
  GiChemicalDrop, 
  GiThermometerHot, 
  GiDroplets,  // Replaced GiHumidity with GiDroplets
  GiWaterSplash
} from 'react-icons/gi';
import './SensorGrid.css';

const SensorGrid = ({ data }) => {
  const getStatusClass = (value, thresholds) => {
    if (value > thresholds.high) return 'high';
    if (value < thresholds.low) return 'low';
    return 'normal';
  };

  return (
    <div className="sensor-grid card">
      <h2 className="section-title">Environmental Sensors</h2>
      <div className="sensors-container">
        {/* ... other sensor cards ... */}
        
        <div className="sensor-card">
          <div className="sensor-icon">
            <GiDroplets />  {/* Changed to GiDroplets */}
          </div>
          <div className="sensor-info">
            <h3>Humidity</h3>
            <div className="sensor-value">{data.humidity}%</div>
            <div className="sensor-range">Optimal: 60-80%</div>
          </div>
        </div>
        
        {/* ... leak detection card ... */}
      </div>
    </div>
  );
};

export default SensorGrid;