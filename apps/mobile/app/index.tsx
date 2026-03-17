import { Redirect } from "expo-router";
import { useAuth } from "../lib/auth-context";

export default function Index() {
  const { accessToken, isReady } = useAuth();

  if (!isReady) return null;
  if (accessToken) return <Redirect href="/(tabs)" />;
  return <Redirect href="/(auth)/login" />;
}
