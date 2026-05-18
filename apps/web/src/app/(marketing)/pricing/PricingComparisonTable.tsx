'use client';

import { Check, Minus } from 'lucide-react';
import {
  PLAN_COMPARISON_ROWS,
  PLAN_COMPARISON_MATRIX,
  DEFAULT_PLANS,
  type PlanSlug,
} from '@/content/pricing-copy';

const PLAN_ORDER: PlanSlug[] = ['free', 'starter', 'pro', 'studio'];

const STORY_ENGINE_ROWS = ['story_integrity', 'story_density'];
const STUDIO_ROWS = [
  'citation_system',
  'bibliography',
  'academic_templates',
  'originality_review',
  'ai_insights',
];

function CellValue({
  val,
}: {
  val: boolean | string;
}) {
  if (val === true) {
    return <Check className="mx-auto h-5 w-5 text-primary" />;
  }
  if (val === false) {
    return <Minus className="mx-auto h-4 w-4 text-muted-foreground/40" />;
  }
  return (
    <span className="text-sm font-medium text-muted-foreground">{String(val)}</span>
  );
}

export function PricingComparisonTable() {
  const storyRows = PLAN_COMPARISON_ROWS.filter((r) =>
    STORY_ENGINE_ROWS.includes(r.key)
  );
  const studioRows = PLAN_COMPARISON_ROWS.filter((r) =>
    STUDIO_ROWS.includes(r.key)
  );
  const otherRows = PLAN_COMPARISON_ROWS.filter(
    (r) =>
      !STORY_ENGINE_ROWS.includes(r.key) && !STUDIO_ROWS.includes(r.key)
  );
  const orderedRows = [...storyRows, ...studioRows, ...otherRows];

  return (
    <section
      id="compare-plans"
      className="py-20 border-t border-white/[0.06]"
      data-analytics="plan-comparison"
    >
      <div className="text-center">
        <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
          Compare plans
        </h2>
        <p className="mt-2 text-muted-foreground">
          See what each plan includes. Citation, academic templates, and originality review are Studio.
        </p>
      </div>

      {/* Desktop table */}
      <div className="mt-10 overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0 lg:overflow-visible">
        <div className="hidden rounded-2xl border border-white/[0.08] bg-card shadow-[var(--shadow-card-premium)] lg:block">
          <div className="overflow-x-auto lg:overflow-visible">
            <table className="w-full min-w-[700px] text-sm">
            <thead>
              <tr className="border-b border-white/[0.08] bg-white/[0.02]">
                <th className="sticky left-0 z-10 min-w-[200px] bg-white/[0.02] px-6 py-4 text-left font-semibold text-foreground backdrop-blur-sm">
                  Feature
                </th>
                {PLAN_ORDER.map((slug) => (
                  <th
                    key={slug}
                    className="min-w-[100px] px-4 py-4 text-center font-semibold text-foreground"
                  >
                    {DEFAULT_PLANS[slug].name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {orderedRows.map((row, idx) => {
                const isStoryEngine = STORY_ENGINE_ROWS.includes(row.key);
                const isStudio = STUDIO_ROWS.includes(row.key);
                return (
                  <tr
                    key={row.key}
                    className={`border-b border-white/[0.04] transition-colors hover:bg-white/[0.02] ${
                      isStoryEngine ? 'bg-primary/[0.04]' : ''
                    } ${isStudio ? 'bg-primary/[0.02]' : ''}`}
                  >
                    <td className="sticky left-0 z-10 min-w-[200px] bg-inherit px-6 py-3 backdrop-blur-sm">
                      <span
                        className={
                          isStoryEngine || isStudio
                            ? 'font-semibold text-foreground'
                            : 'text-muted-foreground'
                        }
                      >
                        {row.label}
                        {isStoryEngine && (
                          <span className="ml-1.5 text-xs text-primary">Pro+</span>
                        )}
                        {isStudio && (
                          <span className="ml-1.5 text-xs text-primary">Studio</span>
                        )}
                      </span>
                    </td>
                    {PLAN_ORDER.map((slug) => {
                      const val = PLAN_COMPARISON_MATRIX[slug]?.[row.key];
                      return (
                        <td key={slug} className="px-4 py-3 text-center">
                          <CellValue val={val as boolean | string} />
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Mobile: plan cards with feature lists */}
      <div className="mt-10 space-y-6 lg:hidden">
        {PLAN_ORDER.map((slug) => (
          <div
            key={slug}
            className="rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)]"
          >
            <h3 className="font-serif text-lg font-semibold text-foreground">
              {DEFAULT_PLANS[slug].name}
            </h3>
            <p className="mt-1 text-xs text-muted-foreground">
              {DEFAULT_PLANS[slug].valueNote}
            </p>
            <ul className="mt-4 space-y-2">
              {orderedRows.map((row) => {
                const val = PLAN_COMPARISON_MATRIX[slug]?.[row.key];
                const isStoryEngine = STORY_ENGINE_ROWS.includes(row.key);
                const isStudio = STUDIO_ROWS.includes(row.key);
                if (val === false) return null;
                return (
                  <li
                    key={row.key}
                    className={`flex items-center gap-2 text-sm ${
                      isStoryEngine || isStudio
                        ? 'font-medium text-foreground'
                        : 'text-muted-foreground'
                    }`}
                  >
                    <Check className="h-4 w-4 shrink-0 text-primary" />
                    {val === true ? row.label : `${row.label}: ${String(val)}`}
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>

      <div className="mt-8 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
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
