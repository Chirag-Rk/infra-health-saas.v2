import { create } from "zustand";

import type {
  SensorData,
  AlertData,
} from "../types/sensor";
interface MonitoringState {
  sensorData: SensorData | null;
  alert: AlertData | null;

  setSensorData: (data: SensorData) => void;
  setAlert: (alert: AlertData | null) => void;
}

export const useMonitoringStore = create<MonitoringState>((set) => ({
  sensorData: null,
  alert: null,

  setSensorData: (data) =>
    set({
      sensorData: data,
    }),

  setAlert: (alert) =>
    set({
      alert,
    }),
}));