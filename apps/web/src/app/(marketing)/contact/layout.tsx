import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Contact | AUTHORA',
  description: 'Get in touch with the AUTHORA team. Questions, feedback, or support.',
};

export default function ContactLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
