/**
 * API proxy for local dev - forwards /api/v1/* to the backend using Node http.
 * Avoids fetch() Expect header issues in Node/undici.
 */
import { NextRequest, NextResponse } from 'next/server';
import http from 'http';

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

function proxyHttp(
  targetUrl: string,
  method: string,
  headers: Record<string, string>,
  body?: string
): Promise<{ status: number; body: string; contentType: string }> {
  return new Promise((resolve, reject) => {
    const url = new URL(targetUrl);
    const req = http.request(
      {
        hostname: url.hostname,
        port: url.port || 80,
        path: url.pathname + url.search,
        method,
        headers: {
          ...headers,
          host: url.host,
        },
      },
      (res) => {
        const chunks: Buffer[] = [];
        res.on('data', (chunk) => chunks.push(chunk));
        res.on('end', () => {
          resolve({
            status: res.statusCode || 500,
            body: Buffer.concat(chunks).toString('utf8'),
            contentType: res.headers['content-type'] || 'application/json',
          });
        });
      }
    );
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
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

  const headers: Record<string, string> = {};
  ['content-type', 'authorization', 'accept'].forEach((k) => {
    const v = request.headers.get(k);
    if (v) headers[k] = v;
  });

  let body: string | undefined;
  if (method !== 'GET' && method !== 'HEAD') {
    body = await request.text();
  }

  try {
    const { status, body: resBody, contentType } = await proxyHttp(target, method, headers, body);
    let json: unknown;
    try {
      json = resBody ? JSON.parse(resBody) : {};
    } catch {
      json = { detail: resBody || 'Unknown error' };
    }
    return NextResponse.json(json, {
      status,
      headers: { 'Content-Type': contentType },
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
