import type { MonitoringPayload } from "../types/sensor";

export const connectWebSocket = (
  onMessage: (data: MonitoringPayload) => void
) => {
  const ws = new WebSocket(
    "ws://127.0.0.1:8000/ws/stream"
  );

  ws.onopen = () => {
    console.log("WebSocket Connected");
  };

  ws.onmessage = (event) => {
    const data: MonitoringPayload = JSON.parse(event.data);

    onMessage(data);
  };

  ws.onclose = () => {
    console.log("WebSocket Disconnected");
  };

  return ws;
};