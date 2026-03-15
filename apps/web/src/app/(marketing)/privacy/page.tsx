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
        Last updated: March 15, 2025
      </p>
      <div className="mt-12 prose-sanctuary space-y-6">
        <p>
          AUTHORA (&quot;we&quot;, &quot;our&quot;, or &quot;us&quot;) is committed to protecting your privacy. This policy describes how we collect, use, and safeguard your information when you use our services.
        </p>

        <h2>Information We Collect</h2>
        <p>
          We collect information you provide directly when you register, use our services, or contact us:
        </p>
        <ul>
          <li><strong>Account information:</strong> name, email address, password (hashed)</li>
          <li><strong>Content:</strong> manuscripts, chapters, notes, and other writing you create</li>
          <li><strong>Usage data:</strong> writing sessions, goals, and preferences</li>
          <li><strong>Marketing:</strong> lead capture forms (email, name, company, use case) when you subscribe or request a demo</li>
        </ul>

        <h2>How We Use Your Information</h2>
        <p>
          We use your information to provide and improve our services, including:
        </p>
        <ul>
          <li>Providing the writing studio, AI features, and export functionality</li>
          <li>Storing and syncing your manuscripts and content</li>
          <li>Personalizing your experience (accountability, gamification, reminders)</li>
          <li>Communicating with you about your account or support requests</li>
          <li>Sending updates about your subscription or product (if you opt in)</li>
          <li>Ensuring security and preventing abuse</li>
        </ul>

        <h2>AI and Third-Party Services</h2>
        <p>
          When you use AI features (e.g., rewrite, expand, ghostwriter), we may send your text to our configured AI providers (e.g., OpenAI, Anthropic). These providers process data according to their own privacy policies. We do not store AI prompts or responses beyond what is necessary for the session.
        </p>

        <h2>Data Retention</h2>
        <p>
          We retain your content for as long as your account is active. You may delete your account and associated data at any time. We may retain backups for a limited period for recovery purposes.
        </p>

        <h2>Information Sharing</h2>
        <p>
          We do not sell your personal information. We may share data only with service providers who assist in operating our infrastructure (e.g., hosting, storage) under strict confidentiality agreements.
        </p>

        <h2>Security</h2>
        <p>
          We use industry-standard measures to protect your data, including encryption in transit and at rest, secure authentication, and access controls.
        </p>

        <h2>Your Rights</h2>
        <p>
          Depending on your jurisdiction, you may have rights to access, correct, delete, or export your data. Contact us to exercise these rights.
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
