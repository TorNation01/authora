import type { Metadata } from 'next';
import Script from 'next/script';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from '@/components/ui/toaster';
import { ConfigProvider } from '@/contexts/ConfigProvider';
import { ThemeProvider } from '@/contexts/ThemeProvider';
import { TooltipProvider } from '@/components/ui/tooltip';

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
});

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  viewportFit: 'cover',
};

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_MARKETING_URL || process.env.NEXT_PUBLIC_WEB_URL || 'https://authora.studio'),
  title: 'Authora — Finally finish the book you’ve been trying to write',
  description:
    'Authora helps you start, structure, write, improve, and finish your book — with AI guidance, smart editing tools, and built-in momentum that keeps you moving.',
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/icon.png', type: 'image/png', sizes: '512x512' },
    ],
    apple: [{ url: '/apple-icon.png', sizes: '180x180' }],
  },
  openGraph: {
    url: '/',
    siteName: 'Authora',
    type: 'website',
    title: 'Authora — Finally finish the book you’ve been trying to write',
    description:
      'AI guidance, smart editing tools, and built-in momentum. No clutter. No guesswork. Just a clear path to a finished book.',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Authora — finish the book you have been trying to write' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Authora — Finally finish the book you’ve been trying to write',
    description:
      'AI guidance, smart editing tools, and built-in momentum. Just a clear path to a finished book.',
    images: ['/og-image.png'],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="font-sans">
        <Script
          id="theme-init"
          strategy="beforeInteractive"
          dangerouslySetInnerHTML={{
            __html: `(function(){var t=localStorage.getItem('authora_theme')||'light';document.documentElement.setAttribute('data-theme',t);})();`,
          }}
        />
        <ThemeProvider>
          <ConfigProvider>
            <TooltipProvider delayDuration={300}>
              {children}
              <Toaster />
            </TooltipProvider>
          </ConfigProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
