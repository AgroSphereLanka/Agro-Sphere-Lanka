// src/components/WaterTankMonitor.js
import React from 'react';
import { GiWaterTank } from 'react-icons/gi';
import './WaterTankMonitor.css';

const WaterTankMonitor = ({ levels }) => {
  const getTankStatus = (level) => {
    if (level > 85) return { class: 'high', label: 'Full' };
    if (level > 40) return { class: 'medium', label: 'Good' };
    return { class: 'low', label: 'Low' };
  };

  return (
    <div className="water-tank-monitor card">
      <h2 className="section-title">Water Tank System</h2>
      <div className="tanks-container">
        {levels.map((level, index) => {
          const status = getTankStatus(level);
          return (
            <div key={index} className="tank-card">
              <div className="tank-header">
                <GiWaterTank className="tank-icon" />
                <h3>Tank {index + 1}</h3>
              </div>
              <div className="tank-gauge">
                <div 
                  className={`water-level ${status.class}`}
                  style={{ height: `${level}%` }}
                >
                  <span className="level-percent">{level}%</span>
                </div>
              </div>
              <div className={`tank-status ${status.class}`}>
                {status.label}
              </div>
            </div>
          );
        })}
      </div>
      
      {levels[1] > 90 && (
        <div className="alert-banner warning">
          <div className="alert-content">
            <strong>Secondary Tank Almost Full!</strong> 
            <span>Activate overflow system to prevent overflow</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default WaterTankMonitor;