import { useEffect } from "react";

import { connectWebSocket } from "../services/websocket";
import { useMonitoringStore } from "../store/useMonitoringStore";
import LiveSensorPanel from "../components/LiveSensorPanel";

const OperationsCenter = () => {
  const setSensorData =
    useMonitoringStore((state) => state.setSensorData);

  const setAlert =
    useMonitoringStore((state) => state.setAlert);

  useEffect(() => {
    const ws = connectWebSocket((payload) => {
      setSensorData(payload.sensor_data);
      setAlert(payload.alert);
    });

    // Cleanup function
    return () => {
      ws.close();
    };
  }, []);

  // UI returned by the component
  return (
    <div>
      <h1>INFRA-HEALTH Operations Center</h1>

      <p>Connected to Live Monitoring Stream</p>

      <LiveSensorPanel />
    </div>
  );
};

export default OperationsCenter;