import type { Metadata } from 'next';
import { HeroSection } from '@/components/marketing/HeroSection';
import { ProblemSection } from '@/components/marketing/ProblemSection';
import { SolutionSection } from '@/components/marketing/SolutionSection';
import { HowItWorksSection } from '@/components/marketing/HowItWorksSection';
import { FeatureDifferentiatorSection } from '@/components/marketing/FeatureDifferentiatorSection';
import { WritingExperienceSection } from '@/components/marketing/WritingExperienceSection';
import { AccountabilitySection } from '@/components/marketing/AccountabilitySection';
import { FlexibilitySection } from '@/components/marketing/FlexibilitySection';
import { UseCasesSection } from '@/components/marketing/UseCasesSection';
import { WhyDifferentSection } from '@/components/marketing/WhyDifferentSection';
import { PricingTeaserSection } from '@/components/marketing/PricingTeaserSection';
import { FAQSection } from '@/components/marketing/FAQSection';
import { CTASection } from '@/components/marketing/CTASection';

export const metadata: Metadata = {
  title: 'Authora | Finally Finish the Book You\'ve Been Trying to Write',
  description:
    'Authora helps you start, structure, write, improve, and finish your book — with AI guidance, smart editing tools, and built-in momentum that keeps you moving.',
  keywords: ['book writing', 'author tool', 'AI writing', 'finish your book', 'writing app', 'novel writing', 'memoir', 'non-fiction', 'manuscript'],
  alternates: { canonical: '/' },
  openGraph: {
    title: 'Authora — Finally finish the book you\'ve been trying to write',
    description: 'AI guidance, smart editing tools, and built-in momentum. No clutter. No guesswork. Just a clear path to a finished book.',
    type: 'website',
    url: '/',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Authora — Finally finish the book you\'ve been trying to write',
    description: 'AI guidance, smart editing tools, and built-in momentum. No clutter. No guesswork. Just a clear path to a finished book.',
  },
};

export default function LandingPage() {
  return (
    <div data-page="landing">
      <HeroSection />
      <ProblemSection />
      <SolutionSection />
      <HowItWorksSection />
      <FeatureDifferentiatorSection />
      <WritingExperienceSection />
      <AccountabilitySection />
      <FlexibilitySection />
      <UseCasesSection />
      <WhyDifferentSection />
      <PricingTeaserSection />
      <FAQSection />
      <CTASection />
    </div>
  );
}
