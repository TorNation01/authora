import { ExpoConfig, ConfigContext } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: "Authora",
  slug: "authora-mobile",
  scheme: "authora",
  version: "1.0.0",
  orientation: "portrait",
  userInterfaceStyle: "automatic",
  ios: {
    supportsTablet: true,
    bundleIdentifier: "com.authora.mobile",
  },
  android: {
    package: "com.authora.mobile",
  },
  plugins: ["expo-router", "expo-secure-store", "expo-notifications"],
});
