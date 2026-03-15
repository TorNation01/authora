import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Privacy Policy | AUTHORA',
  description: 'AUTHORA privacy policy.',
};

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
      <h1 className="font-serif text-4xl font-bold text-foreground">
        Privacy Policy
      </h1>
      <p className="mt-4 text-muted-foreground">
        Last updated: {new Date().toLocaleDateString()}
      </p>
      <div className="mt-12 prose-sanctuary space-y-6">
        <p>
          This is a placeholder for the privacy policy. Please replace with your actual privacy policy content.
        </p>
        <h2>Information we collect</h2>
        <p>
          We collect information you provide when you register, use our services, or contact us. This may include your name, email address, and content you create.
        </p>
        <h2>How we use your information</h2>
        <p>
          We use your information to provide and improve our services, communicate with you, and ensure security.
        </p>
        <h2>Contact</h2>
        <p>
          For privacy-related questions, contact us at{' '}
          <a href="/contact" className="text-primary hover:underline">contact</a>.
        </p>
      </div>
    </div>
  );
}
