import type { Metadata } from 'next';
import { FAQSection } from '@/components/marketing/FAQSection';

export const metadata: Metadata = {
  title: 'FAQ | AUTHORA',
  description: 'Frequently asked questions about AUTHORA—the guided writing platform that helps you finish your book.',
};

const EXTENDED_FAQ = [
  { q: 'What is AUTHORA?', a: 'AUTHORA is a guided writing platform that helps you finish your book. It combines planning tools, a distraction-free editor, AI assistance when you need it, and accountability features—all in one place.' },
  { q: 'How does the AI work?', a: 'AUTHORA\'s AI is built to assist, not replace. You can use it for suggestions, rewrites, expansion, or drafting. You control when and how much AI is involved.' },
  { q: 'How does accountability work?', a: 'Set daily or weekly word goals. Choose your encouragement style—gentle, balanced, or structured. We send reminders and recovery nudges when you\'ve been away.' },
  { q: 'What formats can I export?', a: 'DOCX, PDF, EPUB, and plain text. Export your full manuscript, outline, or individual chapters.' },
  { q: 'Is there a free tier?', a: 'Yes. You can start writing for free. No credit card required.' },
  { q: 'How do I get support?', a: 'Contact us at the link below. We typically respond within 24–48 hours.' },
];

export default function FAQPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
      <h1 className="font-serif text-4xl font-bold text-foreground">
        Frequently asked questions
      </h1>
      <p className="mt-4 text-muted-foreground">
        Everything you need to know about AUTHORA.
      </p>
      <div className="mt-12 space-y-6">
        {EXTENDED_FAQ.map((item, i) => (
          <div key={i} className="border-b border-border/60 pb-6">
            <h2 className="font-semibold text-foreground">{item.q}</h2>
            <p className="mt-2 text-muted-foreground leading-relaxed">{item.a}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
