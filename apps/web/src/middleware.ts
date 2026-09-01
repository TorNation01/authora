/**
 * Host-based routing for Option 2 domain architecture:
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

export function middleware(request: NextRequest) {
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
    return NextResponse.next();
  }

  // On marketing host: redirect app paths to app subdomain
  if (MARKETING_HOSTS.has(hostname)) {
    if (isAppPath(pathname)) {
      const url = new URL(pathname + request.nextUrl.search, `${protocol}://${APP_HOST}`);
      return NextResponse.redirect(url, 301);
    }
    return NextResponse.next();
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
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
