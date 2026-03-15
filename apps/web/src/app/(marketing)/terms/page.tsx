import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Terms of Service | AUTHORA',
  description: 'AUTHORA terms of service.',
};

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
      <h1 className="font-serif text-4xl font-bold text-foreground">
        Terms of Service
      </h1>
      <p className="mt-4 text-muted-foreground">
        Last updated: {new Date().toLocaleDateString()}
      </p>
      <div className="mt-12 prose-sanctuary space-y-6">
        <p>
          This is a placeholder for the terms of service. Please replace with your actual terms.
        </p>
        <h2>Acceptance of terms</h2>
        <p>
          By using AUTHORA, you agree to these terms. If you do not agree, do not use our services.
        </p>
        <h2>Use of service</h2>
        <p>
          You agree to use AUTHORA in compliance with applicable laws and these terms. You retain ownership of your content.
        </p>
        <h2>Contact</h2>
        <p>
          For questions about these terms, contact us at{' '}
          <a href="/contact" className="text-primary hover:underline">contact</a>.
        </p>
      </div>
    </div>
  );
}
