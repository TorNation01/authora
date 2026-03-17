import { getToken } from '@/lib/auth';

const API_BASE = typeof window !== 'undefined' ? (process.env.NEXT_PUBLIC_API_URL || '') : '';

/** Extract readable message from FastAPI error (detail can be string or array of validation objects). */
function getErrorMessage(detail: unknown, fallback: string): string {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0];
    if (first && typeof first === 'object' && 'msg' in first && typeof first.msg === 'string') {
      return first.msg;
    }
    return detail.map((d) => (d && typeof d === 'object' && 'msg' in d ? String(d.msg) : String(d))).join('; ');
  }
  return fallback;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function api<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(getErrorMessage(err.detail, res.statusText), res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function apiUpload<T>(
  path: string,
  file: File,
  extra?: Record<string, string>
): Promise<T> {
  const token = getToken();
  const form = new FormData();
  form.append('file', file);
  if (extra) {
    for (const [k, v] of Object.entries(extra)) {
      form.append(k, v);
    }
  }
  const headers: HeadersInit = {};
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: form,
    headers,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(getErrorMessage(err.detail, res.statusText), res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function apiStream(
  path: string,
  onChunk: (text: string) => void,
  options: RequestInit = {}
): Promise<void> {
  const token = getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) throw new Error(await res.text());
  const reader = res.body?.getReader();
  if (!reader) return;
  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onChunk(decoder.decode(value, { stream: true }));
  }
}
