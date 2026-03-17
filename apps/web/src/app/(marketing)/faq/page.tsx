import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'FAQ | Authora',
  description: 'Frequently asked questions about Authora—the writing platform that helps you finish your book.',
};

const EXTENDED_FAQ = [
  { q: 'Is Authora only for fiction writers?', a: 'No. Authora supports fiction, non-fiction, memoir, workbooks, and more. Built for every kind of writer.' },
  { q: 'Does Authora include a real editor?', a: 'Yes. Authora includes a full manuscript editor designed for book-length writing, with chapters, notes, and revision tools.' },
  { q: 'Can Authora help when I get stuck?', a: 'Yes. AI assistance for brainstorming, rewriting, clarity, and idea generation. Plus structure guidance and manuscript intelligence.' },
  { q: 'Can I use Authora for more than one book?', a: 'Yes. Work on multiple books at once. Different modes and templates per project.' },
  { q: 'Will Authora write the book for me?', a: 'You stay in control. Use AI as much or as little as you want—from light support to ghostwriter-style assistance.' },
  { q: 'Do I need to be a professional writer?', a: 'No. Authora is built for first-time authors and experienced writers alike.' },
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
        Everything you need to know about Authora.
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
