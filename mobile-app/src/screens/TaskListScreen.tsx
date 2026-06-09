import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
} from "react-native";
import { getTasks, updateTaskStatus } from "../lib/api-client";
import { format } from "date-fns";

export default function TaskListScreen({ navigation }: any) {
  const [tasks, setTasks] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = () => getTasks({ status: "pending" }).then(setTasks);

  useEffect(() => { load(); }, []);

  const markDone = async (id: string) => {
    await updateTaskStatus(id, "done");
    load();
  };

  const onRefresh = async () => { setRefreshing(true); await load(); setRefreshing(false); };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Tasks</Text>
      <FlatList
        data={tasks}
        keyExtractor={(t) => t.id}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        renderItem={({ item: t }) => (
          <View style={styles.card}>
            <View style={styles.cardBody}>
              <Text style={styles.taskTitle} numberOfLines={2}>{t.title}</Text>
              <View style={styles.tags}>
                <Text style={styles.tag}>{t.category}</Text>
                <Text style={styles.tag}>{t.urgency}</Text>
              </View>
              {t.due_date && (
                <Text style={styles.due}>Due {format(new Date(t.due_date), "MMM d, HH:mm")}</Text>
              )}
            </View>
            <TouchableOpacity style={styles.doneBtn} onPress={() => markDone(t.id)}>
              <Text style={styles.doneBtnText}>Done</Text>
            </TouchableOpacity>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>No pending tasks</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F9FAFB", padding: 16 },
  title: { fontSize: 20, fontWeight: "bold", color: "#111827", marginBottom: 12 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  cardBody: { flex: 1 },
  taskTitle: { fontSize: 14, fontWeight: "500", color: "#111827" },
  tags: { flexDirection: "row", gap: 6, marginTop: 4 },
  tag: {
    fontSize: 11,
    backgroundColor: "#EEF2FF",
    color: "#4F46E5",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  due: { fontSize: 11, color: "#9CA3AF", marginTop: 2 },
  doneBtn: {
    backgroundColor: "#25D366",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  doneBtnText: { color: "#fff", fontSize: 12, fontWeight: "600" },
  empty: { textAlign: "center", color: "#9CA3AF", marginTop: 40 },
});
