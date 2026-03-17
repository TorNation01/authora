import { View, Text, StyleSheet, Pressable, Alert } from "react-native";
import { router } from "expo-router";
import { useAuth } from "../../lib/auth-context";

export default function SettingsScreen() {
  const { logout } = useAuth();

  async function handleLogout() {
    Alert.alert("Log out", "Are you sure?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Log out",
        style: "destructive",
        onPress: async () => {
          await logout();
          router.replace("/(auth)/login");
        },
      },
    ]);
  }

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>Account</Text>
      <Pressable style={styles.row} onPress={handleLogout}>
        <Text style={styles.rowText}>Log out</Text>
        <Text style={styles.rowChevron}>→</Text>
      </Pressable>
      <Text style={styles.footer}>AUTHORA Mobile • Sync with authora.studio</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  sectionTitle: { fontSize: 14, fontWeight: "600", color: "#666", marginBottom: 12, marginTop: 8 },
  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    backgroundColor: "#fff",
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  rowText: { fontSize: 16 },
  rowChevron: { color: "#999", fontSize: 16 },
  footer: { marginTop: 32, textAlign: "center", color: "#999", fontSize: 14 },
});
