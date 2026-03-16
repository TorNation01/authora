import type { Metadata } from 'next';
import { HeroSection } from '@/components/marketing/HeroSection';
import { ProblemSection } from '@/components/marketing/ProblemSection';
import { SolutionSection } from '@/components/marketing/SolutionSection';
import { HowItWorksSection } from '@/components/marketing/HowItWorksSection';
import { GenresSection } from '@/components/marketing/GenresSection';
import { EditorSection } from '@/components/marketing/EditorSection';
import { AISection } from '@/components/marketing/AISection';
import { AccountabilitySection } from '@/components/marketing/AccountabilitySection';
import { WhyAuthoraSection } from '@/components/marketing/WhyAuthoraSection';
import { TestimonialsSection } from '@/components/marketing/TestimonialsSection';
import { PricingTeaserSection } from '@/components/marketing/PricingTeaserSection';
import { FAQSection } from '@/components/marketing/FAQSection';
import { CTASection } from '@/components/marketing/CTASection';

export const metadata: Metadata = {
  title: 'Authora | Finish the Book',
  description:
    'Authora is the writing studio for fiction and non-fiction authors who want to plan, write, and finish books with structure, accountability, and AI support.',
  keywords: ['book writing', 'author tool', 'AI writing', 'finish your book', 'writing app', 'novel writing', 'memoir', 'non-fiction'],
  openGraph: {
    title: 'Authora — The writing studio that helps you finish the book',
    description: 'Plan clearly, write smoothly, and finish confidently with Authora.',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Authora — The writing studio that helps you finish the book',
    description: 'Plan clearly, write smoothly, and finish confidently with Authora.',
  },
};

export default function LandingPage() {
  return (
    <div data-page="landing">
      <HeroSection />
      <ProblemSection />
      <SolutionSection />
      <HowItWorksSection />
      <GenresSection />
      <EditorSection />
      <AISection />
      <AccountabilitySection />
      <WhyAuthoraSection />
      <TestimonialsSection />
      <PricingTeaserSection />
      <FAQSection />
      <CTASection />
    </div>
  );
}
