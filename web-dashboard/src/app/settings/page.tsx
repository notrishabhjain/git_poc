"use client";

import { useEffect, useState } from "react";
import { getCalendarStatus, getCalendarAuthUrl, triggerCalendarSync } from "@/lib/api-client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SettingsPage() {
  const [bridgeStatus, setBridgeStatus] = useState<any>(null);
  const [calendarConnected, setCalendarConnected] = useState(false);
  const [qrData, setQrData] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    // Check bridge status
    fetch(`${API_URL.replace("/api/v1", "").replace(":8000", ":3001")}/status`)
      .then((r) => r.json())
      .then(setBridgeStatus)
      .catch(() => setBridgeStatus({ connected: false }));

    // Check calendar
    getCalendarStatus().then((s) => setCalendarConnected(s.connected));

    // Get QR if not connected
    fetch(`${API_URL.replace(":8000", ":3001")}/qr`)
      .then((r) => r.json())
      .then((d) => { if (d.qr_data) setQrData(d.qr_data); })
      .catch(() => {});
  }, []);

  const connectCalendar = async () => {
    const { auth_url } = await getCalendarAuthUrl();
    window.open(auth_url, "_blank");
  };

  const syncCalendar = async () => {
    setSyncing(true);
    await triggerCalendarSync();
    setSyncing(false);
    alert("Calendar sync triggered");
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Settings</h1>
        <a href="/" className="text-sm text-gray-500 hover:text-gray-900">← Dashboard</a>
      </div>

      {/* WhatsApp Connection */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-4">
        <h2 className="font-semibold text-gray-900 mb-4">WhatsApp Connection</h2>
        <div className="flex items-center gap-3 mb-4">
          <div
            className={`w-3 h-3 rounded-full ${bridgeStatus?.connected ? "bg-green-500" : "bg-red-500"}`}
          />
          <span className="text-sm text-gray-700">
            {bridgeStatus?.connected ? "Connected" : "Disconnected"}
          </span>
          {bridgeStatus?.lastMessageAt && (
            <span className="text-xs text-gray-400">
              Last message: {new Date(bridgeStatus.lastMessageAt).toLocaleTimeString()}
            </span>
          )}
        </div>
        {!bridgeStatus?.connected && qrData && (
          <div>
            <p className="text-sm text-gray-600 mb-2">
              Scan this QR code with WhatsApp to connect:
            </p>
            <div className="bg-gray-50 p-4 rounded-lg inline-block">
              <pre className="text-xs text-gray-800 whitespace-pre-wrap break-all">{qrData}</pre>
              <p className="text-xs text-gray-500 mt-2">
                Open WhatsApp → Linked Devices → Link a Device → Scan QR
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Google Calendar */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-4">
        <h2 className="font-semibold text-gray-900 mb-4">Google Calendar</h2>
        <div className="flex items-center gap-3 mb-4">
          <div className={`w-3 h-3 rounded-full ${calendarConnected ? "bg-green-500" : "bg-gray-300"}`} />
          <span className="text-sm text-gray-700">
            {calendarConnected ? "Connected" : "Not connected"}
          </span>
        </div>
        <div className="flex gap-3">
          {!calendarConnected && (
            <button
              onClick={connectCalendar}
              className="bg-blue-600 text-white text-sm rounded-lg px-4 py-2 hover:bg-blue-700"
            >
              Connect Google Calendar
            </button>
          )}
          {calendarConnected && (
            <button
              onClick={syncCalendar}
              disabled={syncing}
              className="bg-gray-100 text-gray-700 text-sm rounded-lg px-4 py-2 hover:bg-gray-200 disabled:opacity-50"
            >
              {syncing ? "Syncing…" : "Sync Now"}
            </button>
          )}
        </div>
      </div>

      {/* ntfy.sh setup info */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="font-semibold text-gray-900 mb-3">Push Notifications (ntfy.sh)</h2>
        <p className="text-sm text-gray-600 mb-2">
          Install the <strong>ntfy</strong> app on your phone or browser, then subscribe to your topic:
        </p>
        <code className="text-sm bg-gray-100 px-3 py-1 rounded block">
          {process.env.NTFY_TOPIC || "your-ntfy-topic (set NTFY_TOPIC in .env)"}
        </code>
        <p className="text-xs text-gray-500 mt-2">
          Android: ntfy app | Desktop: ntfy.sh in browser | iOS: ntfy app
        </p>
      </div>
    </div>
  );
}
