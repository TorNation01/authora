import { useState } from "react";
import { View, Text, StyleSheet, TextInput, Pressable, ActivityIndicator, Alert } from "react-native";
import { Link, router } from "expo-router";
import { useAuth } from "../../lib/auth-context";

export default function RegisterScreen() {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleRegister() {
    if (!email.trim() || !password) {
      Alert.alert("Error", "Please enter email and password");
      return;
    }
    if (password.length < 8) {
      Alert.alert("Error", "Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      await register(email.trim(), password, displayName.trim() || undefined);
      router.replace("/(tabs)");
    } catch (e) {
      Alert.alert("Registration failed", e instanceof Error ? e.message : "Please try again");
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create account</Text>
      <TextInput
        style={styles.input}
        placeholder="Display name (optional)"
        value={displayName}
        onChangeText={setDisplayName}
        autoCapitalize="words"
      />
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
        autoComplete="email"
      />
      <TextInput
        style={styles.input}
        placeholder="Password (min 8 characters)"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        autoComplete="password-new"
      />
      <Pressable style={[styles.button, loading && styles.buttonDisabled]} onPress={handleRegister} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Sign up</Text>}
      </Pressable>
      <Link href="/(auth)/login" asChild>
        <Pressable>
          <Text style={styles.link}>Already have an account? Log in</Text>
        </Pressable>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24 },
  title: { fontSize: 24, fontWeight: "600", marginBottom: 24 },
  input: { borderWidth: 1, borderColor: "#ccc", padding: 14, marginBottom: 16, borderRadius: 10, fontSize: 16 },
  button: { backgroundColor: "#007AFF", padding: 16, borderRadius: 10, alignItems: "center", marginBottom: 16, minHeight: 52 },
  buttonDisabled: { opacity: 0.7 },
  buttonText: { color: "#fff", fontWeight: "600", fontSize: 16 },
  link: { color: "#007AFF", textAlign: "center", fontSize: 16 },
});
