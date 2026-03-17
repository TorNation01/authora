/**
 * Push notifications for reminders, streaks, milestones.
 * Registers Expo push token with API on login.
 */

import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import { Platform } from "react-native";
import { api } from "./api";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications(
  accessToken: string
): Promise<string | null> {
  if (!Device.isDevice) return null;

  const { status: existing } = await Notifications.getPermissionsAsync();
  let final = existing;
  if (existing !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    final = status;
  }
  if (final !== "granted") return null;

  const token = (await Notifications.getExpoPushTokenAsync()).data;
  const platform = Platform.OS as "ios" | "android";

  try {
    await api("/api/v1/auth/me/push-token", {
      method: "POST",
      token: accessToken,
      body: JSON.stringify({ token, platform }),
    });
  } catch {
    // Non-fatal: reminders still work in-app
  }

  return token;
}
