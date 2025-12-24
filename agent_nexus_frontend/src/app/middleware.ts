import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { match } from '@formatjs/intl-localematcher';
import Negotiator from 'negotiator';

const i18n = {
  locales: ['en-US', 'es', 'fr'],
  defaultLocale: 'en-US',
};

const protectedPaths = [
  '/agent',
  '/dashboard',
  '/introspection',
  '/settings',
];

function getLocale(request: NextRequest): string {
  const headers = { 'accept-language': request.headers.get('accept-language') || '' };
  const languages = new Negotiator({ headers }).languages();
  const { locales, defaultLocale } = i18n;
  
  return match(languages, locales, defaultLocale);
}

function isAuthenticated(request: NextRequest): boolean {
  const sessionCookie = request.cookies.get('__Secure-next-auth.session-token');
  const token = sessionCookie?.value;

  if (!token) {
    return false;
  }
  
  return true;
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path));
  
  if (isProtectedPath && !isAuthenticated(request)) {
    const loginUrl = new URL(`/login`, request.url);
    loginUrl.searchParams.set('callbackUrl', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  const pathnameIsMissingLocale = i18n.locales.every(
    (locale) => !pathname.startsWith(`/${locale}/`) && pathname !== `/${locale}`
  );

  if (pathnameIsMissingLocale) {
    const locale = getLocale(request);

    if (!pathname.startsWith('/api') && !pathname.includes('.') && pathname !== '/login') {
      return NextResponse.redirect(new URL(`/${locale}${pathname}`, request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|manifest.json|assets|backgrounds|icons).*)',
  ],
};