'use client';

const PAIN_POINTS = [
  'You do not know where to start',
  'You start, then lose momentum',
  'You get stuck in the middle',
  'You rewrite the same chapters over and over',
  'Something feels off, but you do not know what',
  'You never actually finish',
];

export function ProblemSection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="problem">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
          Most people do not fail because they cannot write.
        </h2>
        <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
          They fail because writing a book becomes overwhelming.
        </p>
        <ul className="mt-10 space-y-3 text-left max-w-xl mx-auto">
          {PAIN_POINTS.map((point) => (
            <li key={point} className="flex items-start gap-3 text-muted-foreground">
              <span className="text-primary mt-0.5">•</span>
              {point}
            </li>
          ))}
        </ul>
        <p className="mt-10 font-medium text-foreground">
          Authora solves all of that in one place.
        </p>
      </div>
    </section>
  );
}
