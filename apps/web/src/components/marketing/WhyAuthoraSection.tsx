'use client';

import { FileText, FolderOpen, HelpCircle, Users, CheckCircle } from 'lucide-react';

const VALUE_POINTS = [
  {
    icon: FileText,
    title: 'More structure than a blank document',
  },
  {
    icon: FolderOpen,
    title: 'More focus than scattered notes and folders',
  },
  {
    icon: HelpCircle,
    title: 'More support than a standard writing app',
  },
  {
    icon: Users,
    title: 'More momentum than trying to do it all alone',
  },
  {
    icon: CheckCircle,
    title: 'More completion-focused than generic AI tools',
  },
];

export function WhyAuthoraSection() {
  return (
    <section className="py-20" data-analytics="why-authora">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Why writers choose Authora
          </h2>
        </div>
        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {VALUE_POINTS.map((item) => (
            <div
              key={item.title}
              className="card-sanctuary flex items-start gap-4 p-6"
              data-analytics="why-point"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <item.icon className="h-5 w-5 text-primary" />
              </div>
              <p className="font-medium text-foreground">{item.title}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
