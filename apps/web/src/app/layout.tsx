import type { Metadata } from 'next';
import { Crimson_Pro, Source_Sans_3 } from 'next/font/google';
import './globals.css';
import { Toaster } from '@/components/ui/toaster';
import { ConfigProvider } from '@/contexts/ConfigProvider';
import { TooltipProvider } from '@/components/ui/tooltip';

const sourceSans = Source_Sans_3({
  variable: '--font-source-sans',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
});

const crimson = Crimson_Pro({
  variable: '--font-crimson',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
});

export const metadata: Metadata = {
  title: 'AUTHORA - AI-Powered Book Builder',
  description: 'Your guided writing journey from idea to finished book',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${sourceSans.variable} ${crimson.variable}`} suppressHydrationWarning>
      <body className="font-sans">
        <ConfigProvider>
          <TooltipProvider delayDuration={300}>
            {children}
            <Toaster />
          </TooltipProvider>
        </ConfigProvider>
      </body>
    </html>
  );
}
