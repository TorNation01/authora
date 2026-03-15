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
        Last updated: March 15, 2025
      </p>
      <div className="mt-12 prose-sanctuary space-y-6">
        <p>
          These Terms of Service (&quot;Terms&quot;) govern your use of AUTHORA and related services. By using our services, you agree to these Terms.
        </p>

        <h2>Acceptance of Terms</h2>
        <p>
          By creating an account or using AUTHORA, you agree to these Terms and our Privacy Policy. If you do not agree, do not use our services.
        </p>

        <h2>Eligibility</h2>
        <p>
          You must be at least 18 years old or have parental consent to use AUTHORA. You represent that you have the authority to enter into these Terms.
        </p>

        <h2>Use of Service</h2>
        <p>
          You agree to use AUTHORA in compliance with applicable laws and these Terms. You may not:
        </p>
        <ul>
          <li>Use the service for any illegal purpose or to transmit harmful content</li>
          <li>Attempt to gain unauthorized access to our systems or other users&apos; accounts</li>
          <li>Reverse engineer, decompile, or disassemble the service</li>
          <li>Resell, sublicense, or commercially exploit the service without our written consent</li>
        </ul>

        <h2>Your Content</h2>
        <p>
          You retain ownership of all content you create or upload. By using our service, you grant us a limited license to store, process, and display your content solely to provide the service to you. We do not claim ownership of your manuscripts or other content.
        </p>

        <h2>AI-Generated Content</h2>
        <p>
          AI features may suggest or generate text based on your input. You are responsible for reviewing and editing all AI output before publishing. We do not guarantee accuracy, originality, or suitability of AI-generated content.
        </p>

        <h2>Service Availability</h2>
        <p>
          We strive to maintain high availability but do not guarantee uninterrupted service. We may perform maintenance, updates, or suspend service for operational reasons.
        </p>

        <h2>Termination</h2>
        <p>
          We may suspend or terminate your account for violations of these Terms. You may delete your account at any time. Upon termination, you may lose access to your content; we recommend exporting your data before deletion.
        </p>

        <h2>Disclaimer of Warranties</h2>
        <p>
          The service is provided &quot;as is&quot; without warranties of any kind, express or implied. We disclaim warranties of merchantability, fitness for a particular purpose, and non-infringement.
        </p>

        <h2>Limitation of Liability</h2>
        <p>
          To the maximum extent permitted by law, we shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the service.
        </p>

        <h2>Changes</h2>
        <p>
          We may update these Terms from time to time. We will notify you of material changes via email or in-app notice. Continued use after changes constitutes acceptance.
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
