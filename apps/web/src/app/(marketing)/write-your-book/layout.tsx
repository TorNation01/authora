import type { Metadata } from 'next';

/**
 * Sales landing layout — forces light theme, off-white + orange.
 * Dedicated conversion page; does not replace main website.
 */

export const metadata: Metadata = {
  title: 'Write Your Book | AUTHORA — Actually Finish Your Manuscript',
  description:
    'AI guidance, smart structure, and built-in momentum. Start free. No credit card. Finish the book you\'ve been trying to write.',
  openGraph: {
    title: 'Write Your Book | AUTHORA',
    description: 'Actually finish your manuscript. AI guidance, structure, momentum.',
    url: '/write-your-book',
  },
};

export default function WriteYourBookLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div data-theme="light" className="min-h-screen bg-[#FAFAF8]">
      {children}
    </div>
  );
}
