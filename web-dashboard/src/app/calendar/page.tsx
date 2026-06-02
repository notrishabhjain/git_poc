"use client";

import { useEffect, useState } from "react";
import { getCalendarEvents, triggerCalendarSync } from "@/lib/api-client";
import { format } from "date-fns";

const SYNC_STATUS_COLORS: Record<string, string> = {
  synced: "bg-green-100 text-green-700",
  pending: "bg-yellow-100 text-yellow-700",
  failed: "bg-red-100 text-red-700",
};

export default function CalendarPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const load = () => {
    getCalendarEvents().then((e) => { setEvents(e); setLoading(false); });
  };

  useEffect(() => { load(); }, []);

  const handleSync = async () => {
    setSyncing(true);
    await triggerCalendarSync();
    setTimeout(() => { load(); setSyncing(false); }, 2000);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Calendar Events</h1>
        <div className="flex gap-3">
          <button
            onClick={handleSync}
            disabled={syncing}
            className="text-sm bg-brand text-white rounded-lg px-4 py-2 hover:opacity-90 disabled:opacity-50"
          >
            {syncing ? "Syncing…" : "Sync with Google"}
          </button>
          <a href="/" className="text-sm text-gray-500 hover:text-gray-900 self-center">← Dashboard</a>
        </div>
      </div>
      {loading ? (
        <div className="text-gray-500 text-sm">Loading…</div>
      ) : events.length === 0 ? (
        <div className="text-gray-500 text-sm">No calendar events yet. Tasks with dates will appear here.</div>
      ) : (
        <div className="space-y-3">
          {events.map((e) => (
            <div key={e.id} className="bg-white rounded-xl shadow-sm p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="font-medium text-sm text-gray-900">{e.title}</div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {format(new Date(e.start_time), "MMM d, yyyy HH:mm")} →{" "}
                    {format(new Date(e.end_time), "HH:mm")}
                  </div>
                  {e.location && (
                    <div className="text-xs text-gray-400 mt-0.5">{e.location}</div>
                  )}
                </div>
                <span className={`text-xs px-1.5 py-0.5 rounded flex-shrink-0 ${SYNC_STATUS_COLORS[e.sync_status] || "bg-gray-100"}`}>
                  {e.sync_status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
