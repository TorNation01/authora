import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getHelpPage, HELP_PAGES } from '@/content/help-pages';

interface HelpPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  return HELP_PAGES.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: HelpPageProps): Promise<Metadata> {
  const { slug } = await params;
  const page = getHelpPage(slug);
  if (!page) return { title: 'Help | Authora' };
  return {
    title: `${page.title} | Help | Authora`,
    description: page.description,
  };
}

export default async function HelpPage({ params }: HelpPageProps) {
  const { slug } = await params;
  const page = getHelpPage(slug);
  if (!page) notFound();

  return (
    <article>
      <h1 className="font-serif text-3xl font-bold text-foreground">
        {page.title}
      </h1>
      <p className="mt-2 text-muted-foreground">{page.description}</p>

      <div className="mt-10 space-y-10">
        {page.sections.map((section, i) => (
          <section key={i}>
            <h2 className="font-semibold text-foreground text-lg">
              {section.heading}
            </h2>
            <div className="mt-4 space-y-3">
              {section.body.map((para, j) => (
                <p key={j} className="text-muted-foreground leading-relaxed">
                  {para}
                </p>
              ))}
            </div>
          </section>
        ))}
      </div>
    </article>
  );
}
