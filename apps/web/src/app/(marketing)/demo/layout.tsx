import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Request a Demo | AUTHORA',
  description: 'See AUTHORA in action. Schedule a personalized demo and learn how to finish your book.',
};

export default function DemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
