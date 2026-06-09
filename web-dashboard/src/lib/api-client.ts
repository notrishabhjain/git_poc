import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 15000,
});

// Attach JWT token from localStorage on every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const login = async (password: string) => {
  const { data } = await api.post("/auth/login", { password });
  localStorage.setItem("access_token", data.access_token);
  return data;
};

export const logout = () => {
  localStorage.removeItem("access_token");
};

// Dashboard
export const getDashboardStats = () => api.get("/dashboard/stats").then((r) => r.data);

// Tasks
export const getTasks = (params?: { status?: string; category?: string }) =>
  api.get("/tasks", { params }).then((r) => r.data);

export const createTask = (data: object) => api.post("/tasks", data).then((r) => r.data);

export const updateTaskStatus = (id: string, status: string) =>
  api.patch(`/tasks/${id}/status`, { status }).then((r) => r.data);

// Messages
export const getMessages = (params?: { limit?: number; offset?: number }) =>
  api.get("/messages", { params }).then((r) => r.data);

// Reminders
export const getReminders = () => api.get("/reminders").then((r) => r.data);
export const snoozeReminder = (id: string, minutes: number) =>
  api.post(`/reminders/${id}/snooze`, { minutes }).then((r) => r.data);

// Calendar
export const getCalendarStatus = () => api.get("/calendar/status").then((r) => r.data);
export const getCalendarAuthUrl = () => api.get("/calendar/auth-url").then((r) => r.data);
export const getCalendarEvents = () => api.get("/calendar/events").then((r) => r.data);
export const triggerCalendarSync = () => api.post("/calendar/sync").then((r) => r.data);
