/**
 * Host-based routing for Option 2 domain architecture, plus the top of the
 * funnel: every landing page view is recorded once (anonymous, cookie-scoped)
 * and the cookie id is handed to the register form so a signup can be
 * attributed to the visit that produced it.
 * - authora.studio = marketing only
 * - v2.authora.studio = marketing only (v2 preview)
 * - app.authora.studio = logged-in app (dashboard, auth, setup)
 * - api.authora.studio = backend API (handled by reverse proxy)
 *
 * Local dev (localhost, 127.0.0.1): no redirects.
 */
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const MARKETING_HOST = process.env.NEXT_PUBLIC_MARKETING_URL
  ? new URL(process.env.NEXT_PUBLIC_MARKETING_URL).hostname
  : 'authora.studio';
const APP_HOST = process.env.NEXT_PUBLIC_APP_URL
  ? new URL(process.env.NEXT_PUBLIC_APP_URL).hostname
  : 'app.authora.studio';

// Additional hosts that should serve the marketing site
const MARKETING_HOSTS = new Set([
  MARKETING_HOST,
  'www.authora.studio',
]);

// Standalone preview hosts — serve both marketing and app on one domain (no split-domain redirects)
const STANDALONE_HOSTS = new Set([
  'v2.authora.studio',
]);

const MARKETING_PATHS = ['/', '/features', '/pricing', '/faq', '/contact', '/demo', '/terms', '/privacy'];
const APP_PATHS = ['/dashboard', '/login', '/register', '/sso', '/setup', '/onboarding'];

function isMarketingPath(pathname: string): boolean {
  if (pathname === '/') return true;
  return MARKETING_PATHS.some((p) => pathname === p || pathname.startsWith(p + '/'));
}

function isAppPath(pathname: string): boolean {
  return APP_PATHS.some((p) => pathname === p || pathname.startsWith(p + '/'));
}

// --- Funnel instrumentation -------------------------------------------------
// Where the API lives from inside this container. Same box, loopback port.
const API_INTERNAL = process.env.API_INTERNAL_URL || 'http://127.0.0.1:8004';
const VISITOR_COOKIE = 'av_id';

// Only top-of-funnel pages count as a "visit". The dashboard is a logged-in
// app view, not acquisition traffic, so it stays out of the denominator.
function shouldTrack(pathname: string): boolean {
  if (pathname.startsWith('/dashboard')) return false;
  return isMarketingPath(pathname) || isAppPath(pathname);
}

function isValidVisitor(id: string | undefined): id is string {
  return !!id && /^[A-Za-z0-9_-]{8,64}$/.test(id);
}

async function sendVisit(request: NextRequest, visitorId: string): Promise<void> {
  const payload = {
    path: request.nextUrl.pathname,
    referrer: request.headers.get('referer') || null,
    visitor_id: visitorId,
    utm_source: request.nextUrl.searchParams.get('utm_source'),
    utm_medium: request.nextUrl.searchParams.get('utm_medium'),
    utm_campaign: request.nextUrl.searchParams.get('utm_campaign'),
  };
  try {
    // Bounded: a slow analytics write must never hold the page. The API is on
    // loopback, so this is normally single-digit milliseconds.
    await fetch(`${API_INTERNAL}/api/v1/analytics/visit`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'user-agent': request.headers.get('user-agent') || '',
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(400),
    });
  } catch {
    // Analytics is not allowed to be the reason a page fails.
  }
}

async function withVisit(
  request: NextRequest,
  response: NextResponse,
  hostname: string
): Promise<NextResponse> {
  const existing = request.cookies.get(VISITOR_COOKIE)?.value;
  const visitorId = isValidVisitor(existing) ? existing : crypto.randomUUID();

  if (!isValidVisitor(existing)) {
    response.cookies.set({
      name: VISITOR_COOKIE,
      value: visitorId,
      path: '/',
      maxAge: 60 * 60 * 24 * 365,
      sameSite: 'lax',
      // Read by the register form to attribute the signup — not a secret.
      httpOnly: false,
      secure: request.headers.get('x-forwarded-proto') !== 'http',
      // Shared across authora.studio and app.authora.studio so a visitor who
      // lands on marketing and signs up on the app subdomain keeps one id.
      domain: hostname.endsWith('authora.studio') ? '.authora.studio' : undefined,
    });
  }

  if (request.method === 'GET' && shouldTrack(request.nextUrl.pathname)) {
    await sendVisit(request, visitorId);
  }

  return response;
}

export async function middleware(request: NextRequest): Promise<NextResponse> {
  const host = request.headers.get('host') || '';
  const hostname = host.split(':')[0];
  const pathname = request.nextUrl.pathname;

  // Skip API routes, static files, _next
  if (
    pathname.startsWith('/api/') ||
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/favicon') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // Local dev: no host-based redirects
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return NextResponse.next();
  }

  const protocol = request.headers.get('x-forwarded-proto') || 'https';

  // Standalone preview hosts: serve everything — no split-domain redirects
  if (STANDALONE_HOSTS.has(hostname)) {
    return withVisit(request, NextResponse.next(), hostname);
  }

  // On marketing host: redirect app paths to app subdomain
  if (MARKETING_HOSTS.has(hostname)) {
    if (isAppPath(pathname)) {
      const url = new URL(pathname + request.nextUrl.search, `${protocol}://${APP_HOST}`);
      return NextResponse.redirect(url, 301);
    }
    return withVisit(request, NextResponse.next(), hostname);
  }

  // On app host: redirect marketing paths to marketing subdomain; app root -> dashboard
  if (hostname === APP_HOST) {
    if (isMarketingPath(pathname)) {
      if (pathname === '/') {
        const url = new URL('/dashboard', `${protocol}://${APP_HOST}`);
        return NextResponse.redirect(url, 302);
      }
      const url = new URL(pathname + request.nextUrl.search, `${protocol}://${MARKETING_HOST}`);
      return NextResponse.redirect(url, 301);
    }
    return withVisit(request, NextResponse.next(), hostname);
  }

  return withVisit(request, NextResponse.next(), hostname);
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
