/**
 * API proxy for local dev - forwards /api/v1/* to the backend.
 * Ensures registration and all API calls work without CORS when API runs on :8000.
 */
import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, params, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, params, 'POST');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, params, 'PUT');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, params, 'PATCH');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, params, 'DELETE');
}

async function proxy(
  request: NextRequest,
  params: Promise<{ path: string[] }>,
  method: string
) {
  const { path } = await params;
  const pathStr = path.join('/');
  const url = new URL(request.url);
  const target = `${API_URL}/api/v1/${pathStr}${url.search}`;

  const headers = new Headers();
  request.headers.forEach((v, k) => {
    if (!['host', 'connection'].includes(k.toLowerCase())) {
      headers.set(k, v);
    }
  });

  let body: BodyInit | undefined;
  if (method !== 'GET' && method !== 'HEAD') {
    try {
      body = await request.text();
    } catch {
      body = undefined;
    }
  }

  try {
    const res = await fetch(target, {
      method,
      headers,
      body: body || undefined,
    });

    const resBody = await res.text();
    let json: unknown;
    try {
      json = resBody ? JSON.parse(resBody) : undefined;
    } catch {
      json = { detail: resBody || res.statusText };
    }

    return NextResponse.json(json ?? {}, {
      status: res.status,
      headers: {
        'Content-Type': res.headers.get('Content-Type') || 'application/json',
      },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Failed to reach API';
    console.error('[API proxy]', target, err);
    return NextResponse.json(
      { detail: `API unreachable: ${msg}. Is the API running on ${API_URL}?` },
      { status: 503 }
    );
  }
}
