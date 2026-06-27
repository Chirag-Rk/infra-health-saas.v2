export interface SensorMetrics {
  vibration: number;
  stress: number;
  temperature: number;
}

export interface SensorData {
  asset_id: string;
  asset_name: string;
  timestamp: number;

  metrics: SensorMetrics;

  risk_score: number;

  status: "healthy" | "warning" | "critical";
}

export interface AlertData {
  severity: "warning" | "critical";
  message: string;
}

export interface MonitoringPayload {
  sensor_data: SensorData;
  alert: AlertData | null;
}