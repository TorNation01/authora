'use client';

import { Check, Minus } from 'lucide-react';
import {
  PLAN_COMPARISON_ROWS,
  PLAN_COMPARISON_MATRIX,
  DEFAULT_PLANS,
  type PlanSlug,
} from '@/content/pricing-copy';

const PLAN_ORDER: PlanSlug[] = ['free', 'starter', 'pro', 'studio', 'founder_lifetime'];

export function PricingComparisonTable() {
  return (
    <section id="compare-plans" className="py-20" data-analytics="plan-comparison">
      <h2 className="font-serif text-2xl font-bold text-center text-foreground sm:text-3xl">
        Compare plans
      </h2>
      <p className="mt-2 text-center text-muted-foreground">
        See what each plan includes.
      </p>
      <div className="mt-8 overflow-x-auto">
        <table className="w-full min-w-[700px] text-sm">
          <thead>
            <tr className="border-b border-border/60">
              <th className="px-4 py-3 text-left font-medium text-foreground">Feature</th>
              {PLAN_ORDER.map((slug) => (
                <th key={slug} className="px-4 py-3 text-center font-medium text-foreground">
                  {DEFAULT_PLANS[slug].name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {PLAN_COMPARISON_ROWS.map((row) => (
              <tr key={row.key} className="border-b border-border/40">
                <td className="px-4 py-3 text-muted-foreground">{row.label}</td>
                {PLAN_ORDER.map((slug) => {
                  const val = PLAN_COMPARISON_MATRIX[slug]?.[row.key];
                  return (
                    <td key={slug} className="px-4 py-3 text-center">
                      {val === true ? (
                        <Check className="mx-auto h-5 w-5 text-primary" />
                      ) : val === false ? (
                        <Minus className="mx-auto h-4 w-4 text-muted-foreground/50" />
                      ) : (
                        <span className="text-muted-foreground">{String(val)}</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-6 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
        {(Object.entries(DEFAULT_PLANS) as [PlanSlug, (typeof DEFAULT_PLANS)[PlanSlug]][]).map(
          ([slug, def]) => (
            <span key={slug}>
              <strong className="text-foreground">{def.name}</strong> — {def.valueNote}
            </span>
          )
        )}
      </div>
    </section>
  );
}
