'use client';

import { Quote } from 'lucide-react';

const TESTIMONIALS = [
  {
    quote: 'Authora helped me stop circling the same idea and finally start making real progress.',
    author: 'Author',
    role: 'First-time author',
    avatar: null,
  },
  {
    quote: 'The structure, reminders, and AI support made writing feel possible again.',
    author: 'Author',
    role: 'Memoir writer',
    avatar: null,
  },
  {
    quote: 'This feels like the first tool that actually wants me to finish the manuscript.',
    author: 'Author',
    role: 'Fiction writer',
    avatar: null,
  },
];

export function TestimonialsSection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="testimonials">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Built for real writers
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            From first-time authors to experienced writers, Authora is designed for people who want a
            better way to turn ideas into finished books.
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
          Placeholder testimonials. Add verified quotes as you collect them.
        </p>
      </div>
    </section>
  );
}
