"use client";

import { useEffect, useState } from "react";
import { getDashboardStats, getTasks, getMessages } from "@/lib/api-client";
import { format } from "date-fns";

const CATEGORY_COLORS: Record<string, string> = {
  work: "bg-blue-100 text-blue-800",
  personal: "bg-green-100 text-green-800",
  family: "bg-yellow-100 text-yellow-800",
  friends: "bg-purple-100 text-purple-800",
};

const URGENCY_COLORS: Record<string, string> = {
  critical: "bg-red-500",
  high: "bg-orange-400",
  medium: "bg-yellow-400",
  low: "bg-gray-300",
};

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getDashboardStats(),
      getTasks({ status: "pending" }),
      getMessages({ limit: 10 }),
    ]).then(([s, t, m]) => {
      setStats(s);
      setTasks(t.slice(0, 5));
      setMessages(m.slice(0, 5));
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-500">Loading dashboard…</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-900">WhatsApp AI Assistant</h1>
        <nav className="flex gap-4 text-sm font-medium text-gray-600">
          <a href="/tasks" className="hover:text-brand">Tasks</a>
          <a href="/messages" className="hover:text-brand">Messages</a>
          <a href="/calendar" className="hover:text-brand">Calendar</a>
          <a href="/reminders" className="hover:text-brand">Reminders</a>
          <a href="/settings" className="hover:text-brand">Settings</a>
        </nav>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {[
          { label: "Created Today", value: stats?.tasks_created_today ?? 0 },
          { label: "Pending", value: stats?.tasks_pending ?? 0 },
          { label: "Overdue", value: stats?.tasks_overdue ?? 0, warn: true },
          { label: "Done Today", value: stats?.tasks_completed_today ?? 0, good: true },
          { label: "Reminders (24h)", value: stats?.reminders_upcoming_24h ?? 0 },
          { label: "Messages Today", value: stats?.messages_today ?? 0 },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-xl shadow-sm p-4 text-center">
            <div
              className={`text-3xl font-bold ${
                s.warn ? "text-red-500" : s.good ? "text-green-600" : "text-gray-900"
              }`}
            >
              {s.value}
            </div>
            <div className="text-xs text-gray-500 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top tasks */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-semibold text-gray-900">Top Pending Tasks</h2>
            <a href="/tasks" className="text-xs text-brand hover:underline">View all</a>
          </div>
          {tasks.length === 0 ? (
            <p className="text-sm text-gray-500">No pending tasks.</p>
          ) : (
            <ul className="space-y-3">
              {tasks.map((t) => (
                <li key={t.id} className="flex items-start gap-3">
                  <div className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${URGENCY_COLORS[t.urgency] || "bg-gray-300"}`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">{t.title}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className={`text-xs px-1.5 py-0.5 rounded ${CATEGORY_COLORS[t.category] || "bg-gray-100"}`}>
                        {t.category}
                      </span>
                      {t.due_date && (
                        <span className="text-xs text-gray-400">
                          Due {format(new Date(t.due_date), "MMM d")}
                        </span>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Recent messages */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-semibold text-gray-900">Recent Messages</h2>
            <a href="/messages" className="text-xs text-brand hover:underline">View all</a>
          </div>
          {messages.length === 0 ? (
            <p className="text-sm text-gray-500">No messages yet.</p>
          ) : (
            <ul className="space-y-3">
              {messages.map((m) => (
                <li key={m.id} className="text-sm">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900 truncate max-w-[120px]">
                      {m.push_name || m.sender_jid || "Unknown"}
                    </span>
                    {m.ai_intent && m.ai_intent !== "skipped" && (
                      <span className="text-xs bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded">
                        {m.ai_intent}
                      </span>
                    )}
                    <span className="text-xs text-gray-400 ml-auto flex-shrink-0">
                      {format(new Date(m.timestamp), "HH:mm")}
                    </span>
                  </div>
                  <div className="text-gray-500 truncate mt-0.5">{m.body || m.voice_transcript || "[media]"}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
