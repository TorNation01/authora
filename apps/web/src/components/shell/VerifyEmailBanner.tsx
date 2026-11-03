'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';

/**
 * Shown while an address is unconfirmed.
 *
 * An unverified account can write and export, but checkout is closed server-side
 * until the inbox is proven. The banner exists so that gate never looks like a
 * bug to the customer — with one button to send the link again.
 */
export function VerifyEmailBanner({ email }: { email: string }) {
  const [state, setState] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const [message, setMessage] = useState('');

  async function resend() {
    setState('sending');
    try {
      const res = await api<{ sent: boolean; message: string }>('/api/v1/auth/resend-verification', {
        method: 'POST',
      });
      setState('sent');
      setMessage(res.message || 'Confirmation email sent.');
    } catch (err) {
      setState('error');
      setMessage(err instanceof Error ? err.message : 'Could not send the email. Try again in a minute.');
    }
  }

  return (
    <div className="border-b border-amber-300/60 bg-amber-50 px-4 py-2.5 text-sm text-amber-900">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-3 gap-y-2">
        <span>
          Confirm <strong>{email}</strong> to unlock checkout.
        </span>
        {state === 'sent' || state === 'error' ? (
          <span className="text-amber-800">{message}</span>
        ) : (
          <Button size="sm" variant="outline" onClick={resend} disabled={state === 'sending'}>
            {state === 'sending' ? 'Sending…' : 'Resend link'}
          </Button>
        )}
      </div>
    </div>
  );
}
