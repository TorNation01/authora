'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Mail } from 'lucide-react';

export function NewsletterSection() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setStatus('loading');
    try {
      const res = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, type: 'newsletter' }),
      });
      if (res.ok) {
        setStatus('success');
        setEmail('');
      } else {
        setStatus('error');
      }
    } catch {
      setStatus('error');
    }
  }

  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="newsletter">
      <div className="mx-auto max-w-2xl px-4 text-center sm:px-6 lg:px-8">
        <div className="flex justify-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
            <Mail className="h-7 w-7 text-primary" />
          </div>
        </div>
        <h2 className="mt-6 font-serif text-2xl font-bold text-foreground sm:text-3xl">
          Join the waitlist
        </h2>
        <p className="mt-3 text-muted-foreground">
          Get early access, writing tips, and product updates. No spam.
        </p>
        <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={status === 'loading'}
            className="h-11 min-w-0 sm:max-w-xs"
            data-analytics="newsletter-email"
          />
          <Button type="submit" size="lg" disabled={status === 'loading'}>
            {status === 'loading' ? 'Joining…' : status === 'success' ? 'You\'re in!' : 'Join waitlist'}
          </Button>
        </form>
        {status === 'success' && (
          <p className="mt-3 text-sm text-primary">Thanks! We'll be in touch.</p>
        )}
        {status === 'error' && (
          <p className="mt-3 text-sm text-destructive">Something went wrong. Try again.</p>
        )}
      </div>
    </section>
  );
}
