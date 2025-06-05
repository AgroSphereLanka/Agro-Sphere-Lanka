// src/components/ControlPanel.js
import React, { useState } from 'react';
import { FaWater, FaFilter, FaClock } from 'react-icons/fa';
import './ControlPanel.css';

const ControlPanel = ({ systems, toggleSystem, scheduleTankSwitch, addAlert }) => {
  const [scheduleTime, setScheduleTime] = useState('12:00');
  const [fertilizerAmount, setFertilizerAmount] = useState(0);

  const handleFertilizerAdd = () => {
    if (fertilizerAmount > 0) {
      addAlert(`${fertilizerAmount}L fertilizer added to system`, 'success');
      setFertilizerAmount(0);
    } else {
      addAlert('Please enter a valid fertilizer amount', 'error');
    }
  };

  return (
    <div className="control-panel card">
      <h2 className="section-title">System Controls</h2>
      
      <div className="control-group">
        <div className="control-header">
          <FaWater className="control-icon" />
          <h3>Water Systems</h3>
        </div>
        
        <div className="control-item">
          <label>
            Primary Irrigation System
            <div className="control-description">Main water distribution system</div>
          </label>
          <div 
            className={`switch ${systems.water ? 'on' : 'off'}`}
            onClick={() => toggleSystem('water')}
          >
            <div className="slider" />
            <span className="switch-status">
              {systems.water ? 'ON' : 'OFF'}
            </span>
          </div>
        </div>
        
        <div className="control-item">
          <div className="control-header-sub">
            <FaClock className="control-icon-sub" />
            <h4>Secondary Tank Activation</h4>
          </div>
          <div className="scheduling">
            <input 
              type="time" 
              value={scheduleTime}
              onChange={(e) => setScheduleTime(e.target.value)}
              className="time-input"
            />
            <button 
              className="button button-secondary"
              onClick={() => scheduleTankSwitch(scheduleTime)}
            >
              Schedule Activation
            </button>
          </div>
        </div>
        
        <div className="control-item">
          <button 
            className={`button ${systems.emergency ? 'button-success' : 'button-danger'}`}
            onClick={() => toggleSystem('emergency')}
          >
            {systems.emergency ? 'Deactivate Emergency' : 'Activate Secondary Tank'}
          </button>
          <div className="control-description">
            {systems.emergency 
              ? 'Emergency system is active' 
              : 'Activate in case of overflow'}
          </div>
        </div>
      </div>
      
      <div className="control-divider"></div>
      
      <div className="control-group">
        <div className="control-header">
          <FaFilter className="control-icon" />
          <h3>Fertilizer System</h3>
        </div>
        
        <div className="control-item">
          <label>
            Fertilizer Dispersion
            <div className="control-description">Automated nutrient delivery</div>
          </label>
          <div 
            className={`switch ${systems.fertilizer ? 'on' : 'off'}`}
            onClick={() => toggleSystem('fertilizer')}
          >
            <div className="slider" />
            <span className="switch-status">
              {systems.fertilizer ? 'ON' : 'OFF'}
            </span>
          </div>
        </div>
        
        <div className="control-item">
          <label>Add Fertilizer (Liters)</label>
          <div className="fertilizer-control">
            <input 
              type="number" 
              min="0"
              max="100"
              value={fertilizerAmount}
              onChange={(e) => setFertilizerAmount(e.target.value)}
              className="fertilizer-input"
              placeholder="Enter amount"
            />
            <button 
              className="button button-success"
              onClick={handleFertilizerAdd}
            >
              Add Now
            </button>
          </div>
          <div className="control-description">
            Manually add fertilizer to the system
          </div>
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;