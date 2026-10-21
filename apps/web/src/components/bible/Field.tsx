'use client';

import { ReactNode } from 'react';

const inputClass =
  'w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring';

interface FieldProps {
  label: string;
  question: string;
  value: string;
  onChange: (value: string) => void;
  multiline?: boolean;
  rows?: number;
  placeholder?: string;
  type?: string;
  hint?: ReactNode;
  id?: string;
}

/**
 * A field is a question with somewhere to answer it. The label names the
 * craft element, the question does the work of getting a usable answer.
 */
export function Field({
  label,
  question,
  value,
  onChange,
  multiline,
  rows = 3,
  placeholder,
  type = 'text',
  hint,
  id,
}: FieldProps) {
  const fieldId = id || `field-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;

  return (
    <div className="min-w-0">
      <label htmlFor={fieldId} className="block text-sm font-medium text-foreground">
        {label}
      </label>
      <p className="mb-2 mt-1 text-xs leading-relaxed text-muted-foreground">{question}</p>
      {multiline ? (
        <textarea
          id={fieldId}
          value={value}
          rows={rows}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          className={`${inputClass} resize-y leading-relaxed`}
        />
      ) : (
        <input
          id={fieldId}
          type={type}
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          className={inputClass}
        />
      )}
      {hint ? <div className="mt-1 text-xs text-muted-foreground">{hint}</div> : null}
    </div>
  );
}

export function SectionHeading({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        <h2 className="font-serif text-lg font-semibold text-foreground">{title}</h2>
        {description ? (
          <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}

export function SaveStatus({ state }: { state: 'idle' | 'saving' | 'saved' | 'error' }) {
  if (state === 'idle') return null;
  const text =
    state === 'saving' ? 'Saving…' : state === 'saved' ? 'Saved' : 'Could not save — try again';
  return (
    <span
      className={`text-xs ${state === 'error' ? 'text-destructive' : 'text-muted-foreground'}`}
      role="status"
      aria-live="polite"
    >
      {text}
    </span>
  );
}
