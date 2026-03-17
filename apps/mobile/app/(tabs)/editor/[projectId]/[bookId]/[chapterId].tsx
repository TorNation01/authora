import { useEffect, useState, useCallback, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  Pressable,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { useAuth } from "../../../../../lib/auth-context";
import { api, type Chapter } from "../../../../../lib/api";
import { tiptapToPlainText, plainTextToTiptap } from "../../../../../lib/tiptap";

const DEBOUNCE_MS = 1500;

export default function EditorScreen() {
  const { projectId, bookId, chapterId } = useLocalSearchParams<{
    projectId: string;
    bookId: string;
    chapterId: string;
  }>();
  const { accessToken, refresh } = useAuth();
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [content, setContent] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [distractionFree, setDistractionFree] = useState(false);
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastSavedRef = useRef<string>("");

  const loadChapter = useCallback(async () => {
    if (!projectId || !bookId || !chapterId || !accessToken) return;
    try {
      const book = await api<{ chapters: Chapter[] }>(
        `/api/v1/projects/${projectId}/books/${bookId}`,
        { token: accessToken }
      );
      const ch = book.chapters?.find((c) => c.id === chapterId);
      if (ch) {
        setChapter(ch);
        setTitle(ch.title);
        setContent(tiptapToPlainText(ch.content as Record<string, unknown>));
        lastSavedRef.current = tiptapToPlainText(ch.content as Record<string, unknown>);
      }
    } catch (e) {
      if (e instanceof Error && e.message === "UNAUTHORIZED") {
        const newToken = await refresh();
        if (newToken) loadChapter();
      }
    } finally {
      setLoading(false);
    }
  }, [projectId, bookId, chapterId, accessToken]);

  useEffect(() => {
    loadChapter();
  }, [loadChapter]);

  const save = useCallback(async () => {
    if (!projectId || !bookId || !chapterId || !accessToken) return;
    if (content === lastSavedRef.current) return;
    const tiptap = plainTextToTiptap(content);
    setSaving(true);
    try {
      await api(
        `/api/v1/projects/${projectId}/books/${bookId}/chapters/${chapterId}`,
        {
          method: "PATCH",
          token: accessToken,
          body: JSON.stringify({
            content: tiptap,
            title: title || chapter?.title,
          }),
        }
      );
      lastSavedRef.current = content;
    } catch (e) {
      if (e instanceof Error && e.message === "UNAUTHORIZED") {
        const newToken = await refresh();
        if (newToken) save();
      }
    } finally {
      setSaving(false);
    }
  }, [projectId, bookId, chapterId, accessToken, content, title, chapter?.title]);

  useEffect(() => {
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    if (!content && !title) return;
    saveTimeoutRef.current = setTimeout(save, DEBOUNCE_MS);
    return () => {
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    };
  }, [content, title]);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (!chapter) {
    return (
      <View style={styles.centered}>
        <Text style={styles.error}>Chapter not found</Text>
        <Pressable style={styles.backBtn} onPress={() => router.back()}>
          <Text style={styles.backBtnText}>Go back</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={100}
    >
      {!distractionFree && (
        <View style={styles.header}>
          <Pressable onPress={() => router.back()} style={styles.headerBtn}>
            <Text style={styles.headerBtnText}>← Back</Text>
          </Pressable>
          <Text style={styles.headerTitle} numberOfLines={1}>
            {chapter.title}
          </Text>
          <Pressable
            onPress={() => setDistractionFree(true)}
            style={styles.headerBtn}
          >
            <Text style={styles.headerBtnText}>Focus</Text>
          </Pressable>
        </View>
      )}
      {distractionFree && (
        <Pressable
          style={styles.focusOverlay}
          onPress={() => setDistractionFree(false)}
        >
          <Text style={styles.focusHint}>Tap to show menu</Text>
        </Pressable>
      )}
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {!distractionFree && (
          <TextInput
            style={styles.titleInput}
            value={title}
            onChangeText={setTitle}
            placeholder="Chapter title"
            placeholderTextColor="#999"
          />
        )}
        <TextInput
          style={[styles.editor, distractionFree && styles.editorFocus]}
          value={content}
          onChangeText={setContent}
          placeholder="Start writing..."
          placeholderTextColor="#999"
          multiline
          textAlignVertical="top"
        />
      </ScrollView>
      {!distractionFree && (
        <View style={styles.footer}>
          {saving ? (
            <ActivityIndicator size="small" />
          ) : (
            <Text style={styles.footerText}>Saved</Text>
          )}
          <Text style={styles.wordCount}>
            {content.split(/\s+/).filter(Boolean).length} words
          </Text>
        </View>
      )}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  centered: { flex: 1, justifyContent: "center", alignItems: "center" },
  error: { fontSize: 16, color: "#666", marginBottom: 16 },
  backBtn: { padding: 12, backgroundColor: "#007AFF", borderRadius: 8 },
  backBtnText: { color: "#fff", fontWeight: "600" },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  headerBtn: { padding: 8, minWidth: 60 },
  headerBtnText: { color: "#007AFF", fontSize: 16 },
  headerTitle: { flex: 1, fontSize: 16, fontWeight: "600", textAlign: "center" },
  focusOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: 60,
    zIndex: 10,
    justifyContent: "center",
    alignItems: "center",
  },
  focusHint: { fontSize: 12, color: "#999" },
  scroll: { flex: 1 },
  scrollContent: { padding: 20, paddingBottom: 40 },
  titleInput: {
    fontSize: 24,
    fontWeight: "600",
    marginBottom: 24,
    padding: 0,
  },
  editor: {
    fontSize: 18,
    lineHeight: 28,
    minHeight: 400,
    padding: 0,
  },
  editorFocus: { fontSize: 20, lineHeight: 32 },
  footer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#eee",
  },
  footerText: { fontSize: 14, color: "#666" },
  wordCount: { fontSize: 14, color: "#666" },
});
