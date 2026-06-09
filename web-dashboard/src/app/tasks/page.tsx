"use client";

import { useEffect, useState } from "react";
import { getTasks, updateTaskStatus } from "@/lib/api-client";
import { format } from "date-fns";

const STATUSES = ["pending", "in_progress", "done", "deferred"];
const CATEGORIES = ["work", "personal", "family", "friends"];

export default function TasksPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [filterCategory, setFilterCategory] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    getTasks({
      status: filterStatus || undefined,
      category: filterCategory || undefined,
    }).then((t) => {
      setTasks(t);
      setLoading(false);
    });
  };

  useEffect(() => {
    load();
  }, [filterStatus, filterCategory]);

  const handleStatus = async (id: string, status: string) => {
    await updateTaskStatus(id, status);
    load();
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Tasks</h1>
        <a href="/" className="text-sm text-gray-500 hover:text-gray-900">← Dashboard</a>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6 flex-wrap">
        <select
          className="border rounded-lg px-3 py-1.5 text-sm"
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select
          className="border rounded-lg px-3 py-1.5 text-sm"
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        >
          <option value="">All categories</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="text-gray-500 text-sm">Loading…</div>
      ) : tasks.length === 0 ? (
        <div className="text-gray-500 text-sm">No tasks found.</div>
      ) : (
        <div className="space-y-3">
          {tasks.map((t) => (
            <div key={t.id} className="bg-white rounded-xl shadow-sm p-4 flex items-start gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-medium text-gray-900">{t.title}</span>
                  <span className="text-xs bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded">{t.category}</span>
                  <span className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">{t.intent}</span>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded ${
                      t.urgency === "critical"
                        ? "bg-red-100 text-red-700"
                        : t.urgency === "high"
                        ? "bg-orange-100 text-orange-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {t.urgency}
                  </span>
                </div>
                {t.description && (
                  <div className="text-sm text-gray-500 mt-1 truncate">{t.description}</div>
                )}
                {t.due_date && (
                  <div className="text-xs text-gray-400 mt-1">
                    Due: {format(new Date(t.due_date), "MMM d, yyyy HH:mm")}
                    {t.due_date_flexible && " (approx)"}
                  </div>
                )}
              </div>
              <div className="flex flex-col gap-1">
                {t.status !== "done" && (
                  <button
                    onClick={() => handleStatus(t.id, "done")}
                    className="text-xs bg-green-500 text-white rounded px-2 py-1 hover:bg-green-600"
                  >
                    Done
                  </button>
                )}
                {t.status === "pending" && (
                  <button
                    onClick={() => handleStatus(t.id, "in_progress")}
                    className="text-xs bg-blue-500 text-white rounded px-2 py-1 hover:bg-blue-600"
                  >
                    Start
                  </button>
                )}
                <span className="text-xs text-gray-400 text-center">{t.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
