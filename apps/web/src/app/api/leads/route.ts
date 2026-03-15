import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

// Server-side API URL (use API_URL for Docker internal, NEXT_PUBLIC_API_URL for public)
const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || '';
const LEADS_STORAGE_PATH =
  process.env.LEADS_STORAGE_PATH ||
  path.join(process.cwd(), 'storage', 'leads.jsonl');

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
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
}
