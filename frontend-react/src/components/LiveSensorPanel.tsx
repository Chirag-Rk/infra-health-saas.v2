import { useMonitoringStore } from "../store/useMonitoringStore";

const LiveSensorPanel = () => {
  const sensorData = useMonitoringStore(
    (state) => state.sensorData
  );

  if (!sensorData) {
    return (
      <div className="border rounded-lg p-6">
        Waiting for sensor data...
      </div>
    );
  }

  return (
    <div className="border rounded-xl p-6 shadow-md">

      <h2 className="text-xl font-bold mb-4">
        Live Sensor Data
      </h2>

      <div className="space-y-2">

        <p>
          <strong>Asset:</strong> {sensorData.asset_name}
        </p>

        <p>
          <strong>Status:</strong> {sensorData.status}
        </p>

        <p>
          <strong>Risk Score:</strong> {sensorData.risk_score}
        </p>

        <p>
          <strong>Temperature:</strong>{" "}
          {sensorData.metrics.temperature} °C
        </p>

        <p>
          <strong>Stress:</strong>{" "}
          {sensorData.metrics.stress}
        </p>

        <p>
          <strong>Vibration:</strong>{" "}
          {sensorData.metrics.vibration}
        </p>

      </div>

    </div>
  );
};

export default LiveSensorPanel;