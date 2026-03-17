/**
 * Offline sync: queue writes when offline, flush when online.
 * Uses AsyncStorage for pending changes; conflict resolution via if_unchanged_since.
 */

import AsyncStorage from "@react-native-async-storage/async-storage";

const PENDING_KEY = "authora_pending_writes";
const CACHE_PREFIX = "authora_cache_";

export interface PendingWrite {
  id: string;
  type: "chapter" | "note" | "project";
  path: string;
  method: "PATCH" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  timestamp: number;
  lastKnownUpdate?: string; // ISO string for if_unchanged_since
}

export async function getPendingWrites(): Promise<PendingWrite[]> {
  const raw = await AsyncStorage.getItem(PENDING_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

export async function addPendingWrite(write: Omit<PendingWrite, "id" | "timestamp">): Promise<void> {
  const pending = await getPendingWrites();
  pending.push({
    ...write,
    id: `pw_${Date.now()}_${Math.random().toString(36).slice(2)}`,
    timestamp: Date.now(),
  });
  await AsyncStorage.setItem(PENDING_KEY, JSON.stringify(pending));
}

export async function removePendingWrite(id: string): Promise<void> {
  const pending = await getPendingWrites();
  const next = pending.filter((w) => w.id !== id);
  await AsyncStorage.setItem(PENDING_KEY, JSON.stringify(next));
}

export async function clearPendingWrites(): Promise<void> {
  await AsyncStorage.removeItem(PENDING_KEY);
}

export async function cacheGet<T>(key: string): Promise<T | null> {
  const raw = await AsyncStorage.getItem(CACHE_PREFIX + key);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export async function cacheSet(key: string, value: unknown): Promise<void> {
  await AsyncStorage.setItem(CACHE_PREFIX + key, JSON.stringify(value));
}

export async function cacheRemove(key: string): Promise<void> {
  await AsyncStorage.removeItem(CACHE_PREFIX + key);
}
