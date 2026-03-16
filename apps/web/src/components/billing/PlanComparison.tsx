'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';

interface Plan {
  id: string;
  slug: string;
  name: string;
  limits: Record<string, unknown>;
  features: string[];
}

const FEATURE_LABELS: Record<string, string> = {
  planning: 'Guided planning',
  editor: 'Distraction-free editor',
  notes: 'Notes & research',
  accountability: 'Goals & accountability',
  gamification: 'Celebrations & streaks',
  ai: 'AI assistance',
  ghostwriter: 'Ghostwriter mode',
  export_pdf: 'Export to PDF',
  export_epub: 'Export to EPUB',
  publishing_prep: 'Publishing prep tools',
  finish_mode: 'Finish Mode',
  semantic_search: 'Semantic search / RAG',
  premium_model_routing: 'Premium model routing',
};

export function PlanComparison() {
  const [plans, setPlans] = useState<Plan[]>([]);

  useEffect(() => {
    api<Plan[]>('/api/v1/billing/plans')
      .then(setPlans)
      .catch(() => setPlans([]));
  }, []);

  if (plans.length === 0) return null;

  const allFeatures = Array.from(new Set(plans.flatMap((p) => p.features || []))).sort();
  const orderedPlans = [...plans].sort((a, b) => {
    const order = ['free', 'starter', 'pro', 'studio', 'founder_lifetime'];
    return order.indexOf(a.slug) - order.indexOf(b.slug);
  });

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[500px] text-sm">
        <thead>
          <tr className="border-b">
            <th className="px-4 py-3 text-left font-medium">Feature</th>
            {orderedPlans.map((p) => (
              <th key={p.id} className="px-4 py-3 text-center font-medium">
                {p.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {allFeatures.map((f) => (
            <tr key={f} className="border-b">
              <td className="px-4 py-3 text-muted-foreground">
                {FEATURE_LABELS[f] ?? f}
              </td>
              {orderedPlans.map((p) => (
                <td key={p.id} className="px-4 py-3 text-center">
                  {(p.features || []).includes(f) ? (
                    <Check className="mx-auto h-5 w-5 text-primary" />
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-6 flex justify-center gap-4">
        <Button asChild>
          <Link href="/register">Start free</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/pricing">View pricing</Link>
        </Button>
      </div>
    </div>
  );
}
