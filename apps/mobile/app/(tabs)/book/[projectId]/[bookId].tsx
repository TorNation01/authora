import { useEffect, useState } from "react";
import { View, Text, StyleSheet, FlatList, Pressable, ActivityIndicator } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { useAuth } from "../../../../lib/auth-context";
import { api, type Chapter } from "../../../../lib/api";

interface BookWithChapters {
  id: string;
  title: string;
  chapters: Chapter[];
}

export default function BookChaptersScreen() {
  const { projectId, bookId } = useLocalSearchParams<{ projectId: string; bookId: string }>();
  const { accessToken, refresh } = useAuth();
  const [book, setBook] = useState<BookWithChapters | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!projectId || !bookId || !accessToken) return;
    (async () => {
      try {
        const data = await api<BookWithChapters>(
          `/api/v1/projects/${projectId}/books/${bookId}`,
          { token: accessToken }
        );
        setBook(data);
      } catch (e) {
        if (e instanceof Error && e.message === "UNAUTHORIZED") {
          const newToken = await refresh();
          if (newToken) {
            const data = await api<BookWithChapters>(
              `/api/v1/projects/${projectId}/books/${bookId}`,
              { token: newToken }
            );
            setBook(data);
          }
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [projectId, bookId, accessToken]);

  if (loading || !book) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  const chapters = [...(book.chapters || [])].sort((a, b) => a.sort_order - b.sort_order);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{book.title}</Text>
      <FlatList
        data={chapters}
        keyExtractor={(c) => c.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>No chapters yet.</Text>}
        renderItem={({ item }) => (
          <Pressable
            style={styles.card}
            onPress={() =>
              router.push(`/(tabs)/editor/${projectId}/${bookId}/${item.id}`)
            }
          >
            <Text style={styles.cardTitle}>{item.title}</Text>
            <Text style={styles.cardMeta}>{item.word_count} words</Text>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  centered: { flex: 1, justifyContent: "center", alignItems: "center" },
  title: { fontSize: 20, fontWeight: "600", padding: 16, paddingBottom: 8 },
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
