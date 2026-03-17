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
  title: 'AUTHORA - AI-Powered Book Builder',
  description: 'Your guided writing journey from idea to finished book',
  openGraph: {
    url: '/',
    siteName: 'AUTHORA',
    type: 'website',
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
