import React, { useState, useEffect } from 'react';
import ControlPanel from './ControlPanel';
import SensorGrid from './SensorGrid';
import WaterTankMonitor from './WaterTankMonitor';
import Header from './Header';
import './Dashboard.css';

const Dashboard = ({ addAlert, setIsAuthenticated }) => {
  // State declarations
  const [sensorData, setSensorData] = useState({
    ph: 6.8,
    ec: 2.4,
    temperature: 24.5,
    humidity: 65,
    leakDetected: false
  });

  const [tankLevels, setTankLevels] = useState([85, 35]);
  const [systems, setSystems] = useState({
    water: true,
    fertilizer: false,
    emergency: false
  });

  const [alertHistory, setAlertHistory] = useState({});

  // Function declarations
  const toggleSystem = (system) => {
    setSystems(prev => {
      const newState = { ...prev, [system]: !prev[system] };
      addAlert(`${system.charAt(0).toUpperCase() + system.slice(1)} system ${newState[system] ? 'activated' : 'deactivated'}`);
      return newState;
    });
  };

  const scheduleTankSwitch = (time) => {
    addAlert(`Secondary tank scheduled for activation at ${time}`);
    // Backend integration goes here
  };

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSensorData(prev => ({
        ph: +(prev.ph + (Math.random() * 0.2 - 0.1)).toFixed(2),
        ec: +(prev.ec + (Math.random() * 0.1 - 0.05)).toFixed(2),
        temperature: +(prev.temperature + (Math.random() - 0.5)).toFixed(1),
        humidity: Math.min(95, Math.max(40, prev.humidity + (Math.random() * 4 - 2))),
        leakDetected: Math.random() > 0.9
      }));

      setTankLevels(prev => [
        Math.min(100, prev[0] + (systems.water ? -0.1 : 0.2)),
        Math.min(100, prev[1] + (prev[0] > 20 ? 0.15 : -0.05))
      ]);
    }, 2000);

    return () => clearInterval(interval);
  }, [systems]);

  // Improved tank + leak alerts with history
  useEffect(() => {
    const tankKey = 'tank-alert';
    if (tankLevels[1] >= 95 && !systems.emergency && !alertHistory[tankKey]) {
      addAlert('Secondary tank almost full! Activate overflow protocol', 'warning');
      setAlertHistory(prev => ({ ...prev, [tankKey]: true }));
    } else if (tankLevels[1] < 90 && alertHistory[tankKey]) {
      setAlertHistory(prev => ({ ...prev, [tankKey]: false }));
    }

    const leakKey = 'leak-alert';
    if (sensorData.leakDetected && !alertHistory[leakKey]) {
      addAlert('LEAK DETECTED! Emergency shutdown initiated', 'danger');
      setSystems(prev => ({ ...prev, water: false, emergency: true }));
      setAlertHistory(prev => ({ ...prev, [leakKey]: true }));
    } else if (!sensorData.leakDetected && alertHistory[leakKey]) {
      setAlertHistory(prev => ({ ...prev, [leakKey]: false }));
    }
  }, [tankLevels, sensorData, systems.emergency, alertHistory, addAlert]);

  // Render
  return (
    <div className="dashboard">
      <Header setIsAuthenticated={setIsAuthenticated} />
      <div className="dashboard-grid">
        <div className="dashboard-left">
          <SensorGrid data={sensorData} />
          <WaterTankMonitor levels={tankLevels} />
        </div>
        <div className="dashboard-right">
          <ControlPanel
            systems={systems}
            toggleSystem={toggleSystem}
            scheduleTankSwitch={scheduleTankSwitch}
            addAlert={addAlert}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
