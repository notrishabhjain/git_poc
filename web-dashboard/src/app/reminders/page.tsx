"use client";

import { useEffect, useState } from "react";
import { getReminders, snoozeReminder } from "@/lib/api-client";
import { format } from "date-fns";

export default function RemindersPage() {
  const [reminders, setReminders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    getReminders().then((r) => { setReminders(r); setLoading(false); });
  };

  useEffect(() => { load(); }, []);

  const handleSnooze = async (id: string, minutes: number) => {
    await snoozeReminder(id, minutes);
    load();
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Reminders</h1>
        <a href="/" className="text-sm text-gray-500 hover:text-gray-900">← Dashboard</a>
      </div>
      {loading ? (
        <div className="text-gray-500 text-sm">Loading…</div>
      ) : reminders.length === 0 ? (
        <div className="text-gray-500 text-sm">No reminders scheduled.</div>
      ) : (
        <div className="space-y-3">
          {reminders.map((r) => (
            <div key={r.id} className="bg-white rounded-xl shadow-sm p-4 flex items-start justify-between gap-4">
              <div>
                <div className="font-medium text-sm text-gray-900">{r.title}</div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {format(new Date(r.remind_at), "MMM d, yyyy HH:mm")}
                </div>
                {r.recurrence_rule && (
                  <div className="text-xs text-blue-600 mt-0.5">{r.recurrence_rule}</div>
                )}
                {r.notification_sent && (
                  <div className="text-xs text-green-600 mt-0.5">Notified</div>
                )}
                <div className="text-xs text-gray-400 mt-0.5">
                  Snoozed {r.snooze_count}/{r.max_snoozes}
                </div>
              </div>
              {!r.notification_sent && r.snooze_count < r.max_snoozes && (
                <div className="flex gap-2">
                  {[15, 60].map((min) => (
                    <button
                      key={min}
                      onClick={() => handleSnooze(r.id, min)}
                      className="text-xs bg-gray-100 text-gray-700 rounded px-2 py-1 hover:bg-gray-200"
                    >
                      +{min}m
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
