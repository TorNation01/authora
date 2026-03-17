/**
 * AUTHORA API client for mobile.
 * Uses Bearer token auth; supports refresh on 401.
 */

const getApiUrl = () =>
  process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";

export type TokenPair = { access_token: string; refresh_token: string; expires_in: number };

export async function login(email: string, password: string): Promise<TokenPair> {
  const res = await fetch(`${getApiUrl()}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Login failed: ${res.status}`);
  }
  return res.json();
}

export async function register(
  email: string,
  password: string,
  display_name?: string
): Promise<TokenPair> {
  const res = await fetch(`${getApiUrl()}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, display_name: display_name || email.split("@")[0] }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Registration failed: ${res.status}`);
  }
  return res.json();
}

export async function refreshToken(refresh_token: string): Promise<TokenPair> {
  const res = await fetch(`${getApiUrl()}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token }),
  });
  if (!res.ok) throw new Error("Token refresh failed");
  return res.json();
}

export async function api<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...init } = options;
  const url = path.startsWith("http") ? path : `${getApiUrl()}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(url, { ...init, headers });
  if (res.status === 401) throw new Error("UNAUTHORIZED");
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Types matching API
export interface Project {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  last_accessed_at?: string;
}

export interface Book {
  id: string;
  title: string;
  type: string;
  genre?: string;
  updated_at: string;
}

export interface Chapter {
  id: string;
  book_id: string;
  title: string;
  sort_order: number;
  content: Record<string, unknown>;
  word_count: number;
  updated_at: string;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  book_id?: string;
  updated_at: string;
}
