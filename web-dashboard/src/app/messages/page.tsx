"use client";

import { useEffect, useState } from "react";
import { getMessages } from "@/lib/api-client";
import { format } from "date-fns";

const INTENT_COLORS: Record<string, string> = {
  meeting_request: "bg-purple-100 text-purple-700",
  deadline: "bg-red-100 text-red-700",
  follow_up: "bg-yellow-100 text-yellow-700",
  reminder: "bg-blue-100 text-blue-700",
  task: "bg-indigo-100 text-indigo-700",
  fyi_no_action: "bg-gray-100 text-gray-500",
  social: "bg-green-50 text-green-600",
  skipped: "bg-gray-50 text-gray-400",
};

export default function MessagesPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMessages({ limit: 100 }).then((m) => {
      setMessages(m);
      setLoading(false);
    });
  }, []);

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Messages</h1>
        <a href="/" className="text-sm text-gray-500 hover:text-gray-900">← Dashboard</a>
      </div>

      {loading ? (
        <div className="text-gray-500 text-sm">Loading…</div>
      ) : (
        <div className="space-y-3">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`bg-white rounded-xl shadow-sm p-4 border-l-4 ${
                m.needs_review ? "border-orange-400" : "border-transparent"
              }`}
            >
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span className="font-medium text-sm text-gray-900">
                  {m.push_name || m.sender_jid || "Unknown"}
                </span>
                {m.is_group_message && (
                  <span className="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">group</span>
                )}
                {m.ai_intent && (
                  <span className={`text-xs px-1.5 py-0.5 rounded ${INTENT_COLORS[m.ai_intent] || "bg-gray-100"}`}>
                    {m.ai_intent}
                  </span>
                )}
                {m.ai_category && (
                  <span className="text-xs bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded">{m.ai_category}</span>
                )}
                {m.needs_review && (
                  <span className="text-xs bg-orange-100 text-orange-600 px-1.5 py-0.5 rounded">needs review</span>
                )}
                <span className="text-xs text-gray-400 ml-auto">
                  {format(new Date(m.timestamp), "MMM d HH:mm")}
                </span>
              </div>
              <div className="text-sm text-gray-700">
                {m.body || m.voice_transcript || `[${m.message_type}]`}
              </div>
              {m.ai_confidence !== null && m.ai_confidence !== undefined && (
                <div className="text-xs text-gray-400 mt-1">
                  Confidence: {(m.ai_confidence * 100).toFixed(0)}%
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
