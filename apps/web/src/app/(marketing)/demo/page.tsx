'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function DemoRequestPage() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [form, setForm] = useState({
    name: '',
    email: '',
    company: '',
    useCase: '',
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus('loading');
    try {
      const res = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, type: 'demo_request' }),
      });
      if (res.ok) {
        setStatus('success');
        setForm({ name: '', email: '', company: '', useCase: '' });
      } else {
        setStatus('error');
      }
    } catch {
      setStatus('error');
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6 lg:px-8">
      <h1 className="font-serif text-4xl font-bold text-foreground">
        Request a demo
      </h1>
      <p className="mt-4 text-muted-foreground">
        See AUTHORA in action. We'll walk you through the platform and answer your questions.
      </p>
      <form
        onSubmit={handleSubmit}
        className="mt-12 space-y-6"
        data-analytics="demo-request-form"
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              required
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="Your name"
              className="mt-2"
            />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              placeholder="you@example.com"
              className="mt-2"
            />
          </div>
        </div>
        <div>
          <Label htmlFor="company">Company or organization</Label>
          <Input
            id="company"
            value={form.company}
            onChange={(e) => setForm((f) => ({ ...f, company: e.target.value }))}
            placeholder="Optional"
            className="mt-2"
          />
        </div>
        <div>
          <Label htmlFor="useCase">What are you looking to accomplish?</Label>
          <textarea
            id="useCase"
            value={form.useCase}
            onChange={(e) => setForm((f) => ({ ...f, useCase: e.target.value }))}
            placeholder="e.g. Writing a novel, coaching clients, team collaboration..."
            rows={4}
            className="mt-2 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>
        <Button type="submit" size="lg" disabled={status === 'loading'}>
          {status === 'loading' ? 'Submitting…' : 'Request demo'}
        </Button>
        {status === 'success' && (
          <p className="text-sm text-primary">
            Thanks! We'll be in touch within 1–2 business days to schedule your demo.
          </p>
        )}
        {status === 'error' && (
          <p className="text-sm text-destructive">Something went wrong. Try again.</p>
        )}
      </form>
      <p className="mt-8 text-sm text-muted-foreground">
        Prefer to start on your own?{' '}
        <Link href="/register" className="text-primary hover:underline">
          Create a free account
        </Link>
      </p>
    </div>
  );
}
