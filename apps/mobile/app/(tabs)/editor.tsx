import { View, Text, StyleSheet, Pressable } from "react-native";
import { router } from "expo-router";

export default function EditorScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Write</Text>
      <Text style={styles.subtitle}>
        Select a project and chapter from Projects to start writing.
      </Text>
      <Pressable
        style={styles.button}
        onPress={() => router.push("/(tabs)")}
      >
        <Text style={styles.buttonText}>Go to Projects</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: "center", alignItems: "center" },
  title: { fontSize: 24, fontWeight: "600", marginBottom: 8 },
  subtitle: { fontSize: 16, color: "#666", textAlign: "center", marginBottom: 24 },
  button: { backgroundColor: "#007AFF", padding: 16, borderRadius: 10 },
  buttonText: { color: "#fff", fontWeight: "600" },
});
