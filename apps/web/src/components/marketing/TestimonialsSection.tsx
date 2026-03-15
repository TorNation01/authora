'use client';

import { Quote } from 'lucide-react';

const TESTIMONIALS = [
  {
    quote: 'AUTHORA helped me finally finish my first novel. The accountability and structure kept me on track.',
    author: 'Author name',
    role: 'Fiction writer',
    avatar: null,
  },
  {
    quote: 'I was drowning in notes and drafts. Having everything in one place changed everything.',
    author: 'Author name',
    role: 'Memoir writer',
    avatar: null,
  },
  {
    quote: 'The AI suggestions are helpful without being overwhelming. I stay in control of my voice.',
    author: 'Author name',
    role: 'Business author',
    avatar: null,
  },
];

export function TestimonialsSection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="testimonials">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Authors who finish
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Join writers who are completing their manuscripts.
          </p>
        </div>
        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <div
              key={i}
              className="card-sanctuary p-6"
              data-analytics="testimonial"
            >
              <Quote className="h-8 w-8 text-primary/30" />
              <p className="mt-4 font-serif text-foreground leading-relaxed">
                &ldquo;{t.quote}&rdquo;
              </p>
              <div className="mt-6 flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center text-sm font-medium text-muted-foreground">
                  {t.author.charAt(0)}
                </div>
                <div>
                  <p className="font-medium text-foreground">{t.author}</p>
                  <p className="text-sm text-muted-foreground">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
        <p className="mt-8 text-center text-sm text-muted-foreground">
          Testimonials placeholder—replace with real quotes and photos.
        </p>
      </div>
    </section>
  );
}
