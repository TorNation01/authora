'use client';

import { cn } from '@/lib/utils';

export interface ComparisonRow {
  label: string;
  vs: string;
  authora: string;
}

interface ComparisonTableProps {
  rows: ComparisonRow[];
  className?: string;
}

export function ComparisonTable({ rows, className }: ComparisonTableProps) {
  return (
    <div
      className={cn(
        'overflow-hidden rounded-xl border border-white/[0.08]',
        className
      )}
    >
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-white/[0.08]">
            <th className="px-6 py-4 text-sm font-medium text-muted-foreground">
              —
            </th>
            <th className="px-6 py-4 text-sm font-medium text-muted-foreground">
              Typical
            </th>
            <th className="px-6 py-4 text-sm font-medium text-primary">
              Authora
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              className="border-b border-white/[0.06] last:border-b-0 transition-colors hover:bg-white/[0.02]"
            >
              <td className="px-6 py-4 text-sm font-medium text-foreground">
                {row.label}
              </td>
              <td className="px-6 py-4 text-sm text-muted-foreground line-through">
                {row.vs}
              </td>
              <td className="px-6 py-4 text-sm font-medium text-foreground">
                {row.authora}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
