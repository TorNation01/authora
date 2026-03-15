import { NextRequest, NextResponse } from 'next/server';

// Server-side API URL (use API_URL for Docker internal, NEXT_PUBLIC_API_URL for public)
const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || '';

/**
 * Lead capture API - newsletter, waitlist, demo requests.
 * Proxies to backend API when available; otherwise returns success (form still works).
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

    if (process.env.NODE_ENV === 'development') {
      console.log('[Leads] Captured (no API):', payload);
    }
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
}
