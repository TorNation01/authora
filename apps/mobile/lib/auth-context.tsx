"use client";

import React, { createContext, useContext, useCallback, useState, useEffect } from "react";
import * as SecureStore from "expo-secure-store";
import { login as apiLogin, register as apiRegister, refreshToken } from "./api";

const ACCESS_KEY = "authora_access_token";
const REFRESH_KEY = "authora_refresh_token";

type AuthContextType = {
  accessToken: string | null;
  isReady: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<string | null>;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  const refresh = useCallback(async () => {
    const rt = await SecureStore.getItemAsync(REFRESH_KEY);
    if (!rt) return null;
    try {
      const data = await refreshToken(rt);
      await SecureStore.setItemAsync(ACCESS_KEY, data.access_token);
      await SecureStore.setItemAsync(REFRESH_KEY, data.refresh_token);
      setAccessToken(data.access_token);
      return data.access_token;
    } catch {
      await SecureStore.deleteItemAsync(ACCESS_KEY);
      await SecureStore.deleteItemAsync(REFRESH_KEY);
      setAccessToken(null);
      return null;
    }
  }, []);

  useEffect(() => {
    (async () => {
      const token = await SecureStore.getItemAsync(ACCESS_KEY);
      if (token) {
        setAccessToken(token);
        import("./notifications").then(({ registerForPushNotifications }) =>
          registerForPushNotifications(token)
        );
      }
      setIsReady(true);
    })();
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const data = await apiLogin(email, password);
      await SecureStore.setItemAsync(ACCESS_KEY, data.access_token);
      await SecureStore.setItemAsync(REFRESH_KEY, data.refresh_token);
      setAccessToken(data.access_token);
      // Register push token for reminders (non-blocking)
      import("./notifications").then(({ registerForPushNotifications }) =>
        registerForPushNotifications(data.access_token)
      );
    },
    []
  );

  const registerUser = useCallback(
    async (email: string, password: string, displayName?: string) => {
      const data = await apiRegister(email, password, displayName);
      await SecureStore.setItemAsync(ACCESS_KEY, data.access_token);
      await SecureStore.setItemAsync(REFRESH_KEY, data.refresh_token);
      setAccessToken(data.access_token);
    },
    []
  );

  const logout = useCallback(async () => {
    await SecureStore.deleteItemAsync(ACCESS_KEY);
    await SecureStore.deleteItemAsync(REFRESH_KEY);
    setAccessToken(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        isReady,
        login,
        register: registerUser,
        logout,
        refresh,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
