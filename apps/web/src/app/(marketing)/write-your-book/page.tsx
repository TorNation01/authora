'use client';

import Link from 'next/link';
import { Check, BookOpen, Sparkles, Target, Zap, ArrowRight } from 'lucide-react';
import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';

const TRUST_BADGES = ['Free forever tier', 'No credit card', 'Cancel anytime'];
const FEATURES = [
  {
    icon: BookOpen,
    title: 'Guided structure',
    desc: 'Know exactly what to write next. Templates and frameworks keep you on track.',
  },
  {
    icon: Sparkles,
    title: 'AI that helps, not replaces',
    desc: 'Suggestions, prompts, and feedback — you stay in control of every word.',
  },
  {
    icon: Target,
    title: 'Built-in momentum',
    desc: 'Goals, streaks, and accountability so you actually finish.',
  },
  {
    icon: Zap,
    title: 'Smart editing tools',
    desc: 'Find filler, fix pacing, strengthen prose — without the overwhelm.',
  },
];
const STEPS = [
  { n: 1, title: 'Create your project', desc: 'Pick a template or start from scratch. Fiction, memoir, nonfiction.' },
  { n: 2, title: 'Write with guidance', desc: 'AI prompts, structure, and feedback at every step.' },
  { n: 3, title: 'Finish your manuscript', desc: 'Export to Word, PDF, or publish. Your book, done.' },
];
const TESTIMONIALS = [
  { quote: 'Finally finished my memoir after years of false starts. AUTHORA gave me the structure I needed.', author: 'Sarah M.' },
  { quote: 'The AI doesn\'t write for you — it helps you think. Game changer.', author: 'James T.' },
  { quote: 'I went from 3 chapters to a full draft in 4 months. No more staring at a blank page.', author: 'Elena R.' },
];
const FAQ = [
  { q: 'Is there really a free tier?', a: 'Yes. Start writing with full access to the core tools. No credit card required.' },
  { q: 'Can I export my book?', a: 'Export to Word, PDF, or EPUB. Your manuscript stays yours.' },
  { q: 'Does the AI write my book?', a: 'No. AUTHORA guides, suggests, and helps — you write every word.' },
  { q: 'What if I get stuck?', a: 'Templates, prompts, and AI suggestions keep you moving. Plus built-in accountability.' },
];

export default function WriteYourBookPage() {
  return (
    <div className="bg-[#FAFAF8] text-[#1A1A1A]">
        {/* 1. Hero */}
        <section className="relative overflow-hidden px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="absolute inset-0 bg-gradient-to-b from-[#FF6A2B]/[0.06] via-transparent to-transparent" />
          <div className="relative mx-auto max-w-4xl text-center">
            <p className="mb-4 text-sm font-medium uppercase tracking-wider text-[#FF6A2B]">
              For writers who want to finish
            </p>
            <h1 className="font-serif text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              Write your book.
              <br />
              <span className="text-[#FF6A2B]">Actually finish it.</span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-[#5F5A54]">
              AI guidance, smart structure, and built-in momentum. No clutter. No guesswork. Just a clear path to a finished manuscript.
            </p>
            <div className="mt-10">
              <CTAPair
                primary="start-writing-free"
                secondary="view-pricing"
                microcopy={CTA_MICROCOPY.hero}
                analyticsPrefix="sales-hero-"
              />
            </div>
            <div className="mt-8 flex flex-wrap justify-center gap-6 text-sm text-[#8C857D]">
              {TRUST_BADGES.map((b) => (
                <span key={b} className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-[#00A86B]" />
                  {b}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* 2. Social proof / trust */}
        <section className="border-t border-[#E8E6E1] bg-white px-4 py-12 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-5xl">
            <p className="text-center text-sm font-medium uppercase tracking-wider text-[#8C857D]">
              Writers are finishing books with AUTHORA
            </p>
            <div className="mt-8 grid gap-8 sm:grid-cols-3">
              {TESTIMONIALS.map((t, i) => (
                <blockquote key={i} className="rounded-xl border border-[#E8E6E1] bg-[#FAFAF8] p-6">
                  <p className="text-[#1A1A1A]">&ldquo;{t.quote}&rdquo;</p>
                  <cite className="mt-4 block text-sm text-[#8C857D] not-italic">— {t.author}</cite>
                </blockquote>
              ))}
            </div>
          </div>
        </section>

        {/* 3. Problem */}
        <section className="px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="font-serif text-2xl font-bold sm:text-3xl">
              You&apos;ve started. You&apos;ve stalled. You&apos;ve circled the same chapters for months.
            </h2>
            <p className="mt-6 text-lg text-[#5F5A54]">
              It&apos;s not a lack of ideas. It&apos;s structure, momentum, and knowing what comes next. AUTHORA fixes that.
            </p>
          </div>
        </section>

        {/* 4. Solution / Features */}
        <section className="border-t border-[#E8E6E1] bg-white px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="mx-auto max-w-5xl">
            <h2 className="text-center font-serif text-2xl font-bold sm:text-3xl">
              Everything you need to finish
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-center text-[#5F5A54]">
              Guided structure, AI assistance, and tools that keep you moving.
            </p>
            <div className="mt-12 grid gap-8 sm:grid-cols-2">
              {FEATURES.map((f) => (
                <div key={f.title} className="flex gap-4 rounded-xl border border-[#E8E6E1] bg-[#FAFAF8] p-6">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-[#FF6A2B]/10">
                    <f.icon className="h-6 w-6 text-[#FF6A2B]" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#1A1A1A]">{f.title}</h3>
                    <p className="mt-2 text-[#5F5A54]">{f.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 5. How it works */}
        <section className="px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="mx-auto max-w-4xl">
            <h2 className="text-center font-serif text-2xl font-bold sm:text-3xl">
              How it works
            </h2>
            <div className="mt-12 flex flex-col gap-8 sm:flex-row sm:justify-between">
              {STEPS.map((s) => (
                <div key={s.n} className="flex flex-1 flex-col items-center text-center">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#FF6A2B] text-lg font-bold text-white">
                    {s.n}
                  </div>
                  <h3 className="mt-4 font-semibold text-[#1A1A1A]">{s.title}</h3>
                  <p className="mt-2 text-sm text-[#5F5A54]">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 6. Pricing teaser */}
        <section className="border-t border-[#E8E6E1] bg-white px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="font-serif text-2xl font-bold sm:text-3xl">
              Start free. Upgrade when you&apos;re ready.
            </h2>
            <p className="mt-4 text-[#5F5A54]">
              Full access to core writing tools. No credit card required.
            </p>
            <div className="mt-8">
              <Link
                href="/pricing"
                className="inline-flex items-center gap-2 rounded-lg bg-[#FF6A2B] px-6 py-3 font-medium text-white transition-colors hover:bg-[#E85C1F]"
              >
                View pricing
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* 7. FAQ */}
        <section className="px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="mx-auto max-w-2xl">
            <h2 className="text-center font-serif text-2xl font-bold sm:text-3xl">
              Common questions
            </h2>
            <dl className="mt-12 space-y-8">
              {FAQ.map((item) => (
                <div key={item.q}>
                  <dt className="font-semibold text-[#1A1A1A]">{item.q}</dt>
                  <dd className="mt-2 text-[#5F5A54]">{item.a}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* 8. Final CTA */}
        <section className="border-t border-[#E8E6E1] bg-gradient-to-b from-[#FF6A2B]/[0.06] to-transparent px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="font-serif text-3xl font-bold sm:text-4xl">
              Your book isn&apos;t finished yet — but it can be.
            </h2>
            <p className="mt-6 text-lg text-[#5F5A54]">
              Stop circling. Start finishing.
            </p>
            <div className="mt-10">
              <CTAPair
                primary="start-writing-free"
                secondary="create-first-book"
                microcopy={CTA_MICROCOPY.ctaSection}
                analyticsPrefix="sales-final-"
              />
            </div>
          </div>
        </section>
    </div>
  );
}
