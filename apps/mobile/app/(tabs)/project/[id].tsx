import { useEffect, useState } from "react";
import { View, Text, StyleSheet, FlatList, Pressable, ActivityIndicator } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { useAuth } from "../../../lib/auth-context";
import { api, type Book } from "../../../lib/api";

export default function ProjectBooksScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { accessToken, refresh } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id || !accessToken) return;
    (async () => {
      try {
        const data = await api<Book[]>(`/api/v1/projects/${id}/books`, { token: accessToken });
        setBooks(data || []);
      } catch (e) {
        if (e instanceof Error && e.message === "UNAUTHORIZED") {
          const newToken = await refresh();
          if (newToken) {
            const data = await api<Book[]>(`/api/v1/projects/${id}/books`, { token: newToken });
            setBooks(data || []);
          }
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [id, accessToken]);

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
        data={books}
        keyExtractor={(b) => b.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>No books in this project.</Text>}
        renderItem={({ item }) => (
          <Pressable
            style={styles.card}
            onPress={() => router.push(`/(tabs)/book/${id}/${item.id}`)}
          >
            <Text style={styles.cardTitle}>{item.title}</Text>
            <Text style={styles.cardMeta}>{item.type} • {new Date(item.updated_at).toLocaleDateString()}</Text>
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
