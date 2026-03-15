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
};

export function PlanComparison() {
  const [plans, setPlans] = useState<Plan[]>([]);

  useEffect(() => {
    api<Plan[]>('/api/v1/billing/plans')
      .then(setPlans)
      .catch(() => setPlans([]));
  }, []);

  if (plans.length === 0) return null;

  const allFeatures = Array.from(
    new Set(plans.flatMap((p) => p.features || []))
  ).sort();

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[500px] text-sm">
        <thead>
          <tr className="border-b">
            <th className="text-left py-3 px-4 font-medium">Feature</th>
            {plans.map((p) => (
              <th key={p.id} className="text-center py-3 px-4 font-medium">
                {p.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {allFeatures.map((f) => (
            <tr key={f} className="border-b">
              <td className="py-3 px-4 text-muted-foreground">
                {FEATURE_LABELS[f] ?? f}
              </td>
              {plans.map((p) => (
                <td key={p.id} className="text-center py-3 px-4">
                  {(p.features || []).includes(f) ? (
                    <Check className="h-5 w-5 text-primary mx-auto" />
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
          <Link href="/contact">Contact for Premium</Link>
        </Button>
      </div>
    </div>
  );
}
