import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 15000,
});

api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (password: string) => {
  const { data } = await api.post("/auth/login", { password });
  await AsyncStorage.setItem("access_token", data.access_token);
  return data;
};

export const getTasks = (params?: { status?: string; category?: string }) =>
  api.get("/tasks", { params }).then((r) => r.data);

export const updateTaskStatus = (id: string, status: string) =>
  api.patch(`/tasks/${id}/status`, { status }).then((r) => r.data);

export const getDashboardStats = () => api.get("/dashboard/stats").then((r) => r.data);

export const getMessages = () => api.get("/messages").then((r) => r.data);

export const getReminders = () => api.get("/reminders").then((r) => r.data);

export const snoozeReminder = (id: string, minutes: number) =>
  api.post(`/reminders/${id}/snooze`, { minutes }).then((r) => r.data);
