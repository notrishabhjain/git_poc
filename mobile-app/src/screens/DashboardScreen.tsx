import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { getDashboardStats, getTasks } from "../lib/api-client";
import { format } from "date-fns";

export default function DashboardScreen({ navigation }: any) {
  const [stats, setStats] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    const [s, t] = await Promise.all([
      getDashboardStats(),
      getTasks({ status: "pending" }),
    ]);
    setStats(s);
    setTasks(t.slice(0, 5));
  };

  useEffect(() => { load(); }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  if (!stats) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#25D366" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Text style={styles.title}>Assistant</Text>

      {/* Stats grid */}
      <View style={styles.statsGrid}>
        {[
          { label: "Created Today", value: stats.tasks_created_today },
          { label: "Pending", value: stats.tasks_pending },
          { label: "Overdue", value: stats.tasks_overdue, warn: true },
          { label: "Done Today", value: stats.tasks_completed_today, good: true },
        ].map((s) => (
          <View key={s.label} style={styles.statCard}>
            <Text
              style={[
                styles.statValue,
                s.warn ? styles.warn : s.good ? styles.good : {},
              ]}
            >
              {s.value}
            </Text>
            <Text style={styles.statLabel}>{s.label}</Text>
          </View>
        ))}
      </View>

      {/* Top tasks */}
      <Text style={styles.sectionTitle}>Top Tasks</Text>
      {tasks.map((t) => (
        <TouchableOpacity
          key={t.id}
          style={styles.taskCard}
          onPress={() => navigation.navigate("TaskDetail", { task: t })}
        >
          <View style={[styles.priorityDot, { backgroundColor: getPriorityColor(t.urgency) }]} />
          <View style={styles.taskContent}>
            <Text style={styles.taskTitle} numberOfLines={1}>{t.title}</Text>
            <Text style={styles.taskMeta}>
              {t.category}
              {t.due_date ? ` · Due ${format(new Date(t.due_date), "MMM d")}` : ""}
            </Text>
          </View>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

function getPriorityColor(urgency: string) {
  return { critical: "#EF4444", high: "#F97316", medium: "#FACC15", low: "#D1D5DB" }[urgency] || "#D1D5DB";
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F9FAFB", padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  title: { fontSize: 24, fontWeight: "bold", color: "#111827", marginBottom: 16 },
  statsGrid: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 20 },
  statCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    alignItems: "center",
    width: "48%",
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  statValue: { fontSize: 28, fontWeight: "bold", color: "#111827" },
  statLabel: { fontSize: 11, color: "#6B7280", marginTop: 2 },
  warn: { color: "#EF4444" },
  good: { color: "#10B981" },
  sectionTitle: { fontSize: 16, fontWeight: "600", color: "#111827", marginBottom: 8 },
  taskCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: 8,
    shadowColor: "#000",
    shadowOpacity: 0.04,
    shadowRadius: 3,
    elevation: 1,
  },
  priorityDot: { width: 8, height: 8, borderRadius: 4 },
  taskContent: { flex: 1 },
  taskTitle: { fontSize: 14, fontWeight: "500", color: "#111827" },
  taskMeta: { fontSize: 12, color: "#6B7280", marginTop: 2 },
});
