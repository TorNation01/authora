import { getToken, getRefreshToken, setTokens } from '@/lib/auth';

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

/**
 * A page refresh must never cost the session.
 *
 * The access token lives 60 minutes (config.access_token_expire_minutes) while
 * the refresh token lives 7 days. Before this, any request made after that hour
 * returned 401, the caller wiped both tokens and the user landed back on
 * /login — on a hard refresh that looks like being randomly booted out.
 *
 * One refresh is shared across concurrent 401s, so a dashboard render firing
 * ten requests refreshes once instead of ten times.
 */
let refreshInFlight: Promise<string | null> | null = null;

const NO_RETRY_PATHS = ['/auth/refresh', '/auth/login', '/auth/register', '/auth/logout'];

async function refreshAccessToken(): Promise<string | null> {
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    const refresh = getRefreshToken();
    if (!refresh) return null;
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!res.ok) return null;
      const data = (await res.json()) as { access_token?: string; refresh_token?: string };
      if (!data?.access_token) return null;
      setTokens(data.access_token, data.refresh_token || refresh);
      return data.access_token;
    } catch {
      // A network failure is not proof the session is dead — leave the tokens in
      // place and let the caller surface a retry instead of signing the user out.
      return null;
    }
  })();

  try {
    return await refreshInFlight;
  } finally {
    refreshInFlight = null;
  }
}

function shouldRetry(path: string): boolean {
  return !NO_RETRY_PATHS.some((p) => path.includes(p));
}

async function send(path: string, options: RequestInit, retried: boolean): Promise<Response> {
  const token = getToken();
  const headers: HeadersInit = { ...(options.headers || {}) };
  if (token) (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401 && !retried && shouldRetry(path)) {
    const fresh = await refreshAccessToken();
    if (fresh) return send(path, options, true);
  }
  return res;
}

export async function api<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const res = await send(path, { ...options, headers }, false);
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
  const form = new FormData();
  form.append('file', file);
  if (extra) {
    for (const [k, v] of Object.entries(extra)) {
      form.append(k, v);
    }
  }

  const res = await send(path, { method: 'POST', body: form }, false);
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
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const res = await send(path, { ...options, headers }, false);
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
