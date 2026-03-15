import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

// Server-side API URL (use API_URL for Docker internal, NEXT_PUBLIC_API_URL for public)
const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || '';
const LEADS_STORAGE_PATH =
  process.env.LEADS_STORAGE_PATH ||
  path.join(process.cwd(), 'storage', 'leads.jsonl');

// In-memory rate limit: 5 leads per IP per hour
const LEADS_RATE_LIMIT = 5;
const LEADS_WINDOW_MS = 60 * 60 * 1000;
const _leadsCountByIp: Map<string, { count: number; resetAt: number }> = new Map();

function getClientIp(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  if (forwarded) return forwarded.split(',')[0].trim();
  return request.headers.get('x-real-ip') || '127.0.0.1';
}

function checkLeadsRateLimit(ip: string): boolean {
  const now = Date.now();
  const entry = _leadsCountByIp.get(ip);
  if (!entry) return true;
  if (now > entry.resetAt) {
    _leadsCountByIp.delete(ip);
    return true;
  }
  return entry.count < LEADS_RATE_LIMIT;
}

function recordLeadsRequest(ip: string): void {
  const now = Date.now();
  const entry = _leadsCountByIp.get(ip);
  if (!entry || now > entry.resetAt) {
    _leadsCountByIp.set(ip, { count: 1, resetAt: now + LEADS_WINDOW_MS });
  } else {
    entry.count += 1;
  }
}

async function persistLeadToFile(payload: Record<string, unknown>): Promise<void> {
  const dir = path.dirname(LEADS_STORAGE_PATH);
  await fs.mkdir(dir, { recursive: true });
  const line = JSON.stringify({
    ...payload,
    captured_at: new Date().toISOString(),
  }) + '\n';
  await fs.appendFile(LEADS_STORAGE_PATH, line, 'utf8');
}

/**
 * Lead capture API - newsletter, waitlist, demo requests.
 * Proxies to backend API when available; otherwise persists to file (LEADS_STORAGE_PATH).
 */
export async function POST(request: NextRequest) {
  const ip = getClientIp(request);
  if (!checkLeadsRateLimit(ip)) {
    return NextResponse.json(
      { error: 'Too many requests. Please try again later.' },
      { status: 429, headers: { 'Retry-After': '3600' } }
    );
  }
  try {
    const body = await request.json();
    const { email, type, name, company, message, subject, useCase } = body;

    if (!email || typeof email !== 'string') {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      );
    }

    const payload = {
      email: email.trim().toLowerCase(),
      type: type || 'newsletter',
      name: name?.trim() || null,
      company: company?.trim() || null,
      message: message?.trim() || null,
      subject: subject?.trim() || null,
      useCase: useCase?.trim() || null,
    };

    if (API_URL) {
      const res = await fetch(`${API_URL}/api/v1/leads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        return NextResponse.json(
          { error: err.detail || err.error || 'Failed to save lead' },
          { status: res.status }
        );
      }
      const data = await res.json();
      recordLeadsRequest(ip);
      return NextResponse.json({ success: true, id: data.id });
    }

    // API unavailable: persist to file so leads are not lost
    try {
      await persistLeadToFile(payload);
    } catch (e) {
      console.error('[Leads] Failed to persist to file:', e);
      if (process.env.NODE_ENV === 'development') {
        console.log('[Leads] Captured (fallback failed):', payload);
      }
    }
    recordLeadsRequest(ip);
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
}
