import { useEffect, useState } from "react";
import { View, Text, StyleSheet, FlatList, Pressable, ActivityIndicator, RefreshControl } from "react-native";
import { router } from "expo-router";
import { useAuth } from "../../lib/auth-context";
import { api, type Project } from "../../lib/api";

export default function ProjectsScreen() {
  const { accessToken, refresh } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function load(token: string) {
    try {
      const data = await api<Project[]>("/api/v1/projects", { token });
      setProjects(data || []);
    } catch (e) {
      if (e instanceof Error && e.message === "UNAUTHORIZED") {
        const newToken = await refresh();
        if (newToken) load(newToken);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    if (accessToken) load(accessToken);
  }, [accessToken]);

  async function onRefresh() {
    setRefreshing(true);
    if (accessToken) await load(accessToken);
  }

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={projects}
        keyExtractor={(p) => p.id}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <Text style={styles.empty}>No projects yet. Create one on the web app.</Text>
        }
        renderItem={({ item }) => (
          <Pressable
            style={styles.card}
            onPress={() => router.push(`/(tabs)/project/${item.id}`)}
          >
            <Text style={styles.cardTitle}>{item.name}</Text>
            <Text style={styles.cardMeta}>
              Updated {new Date(item.updated_at).toLocaleDateString()}
            </Text>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  centered: { flex: 1, justifyContent: "center", alignItems: "center" },
  list: { padding: 16, paddingBottom: 32 },
  card: {
    backgroundColor: "#fff",
    padding: 20,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  cardTitle: { fontSize: 18, fontWeight: "600", marginBottom: 4 },
  cardMeta: { fontSize: 14, color: "#666" },
  empty: { textAlign: "center", color: "#666", padding: 32, fontSize: 16 },
});
