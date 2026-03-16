'use client';

export function ProblemSection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="problem">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
          Most people do not struggle to start. They struggle to finish.
        </h2>
        <div className="mt-8 space-y-4 text-lg text-muted-foreground leading-relaxed">
          <p>
            Ideas are not the hard part. The hard part is turning them into a finished manuscript.
            Losing momentum. Getting stuck in the middle. Second-guessing your structure. Starting
            over. Letting a great idea sit unfinished for months or years.
          </p>
          <p className="font-medium text-foreground">
            Authora is built to change that.
          </p>
          <p>
            It brings your planning, drafting, editing support, momentum tools, accountability, and
            AI help into one clear writing space designed to help you keep going.
          </p>
        </div>
      </div>
    </section>
  );
}
