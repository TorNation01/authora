'use client';

import { useState, useRef, useEffect, type KeyboardEvent } from 'react';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { X, ChevronDown, Search } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  category: string;
}

interface MultiSelectProps {
  value: string[];
  onChange: (tags: string[]) => void;
  options: SelectOption[];
  placeholder?: string;
  label?: string;
  className?: string;
}

export function MultiSelect({ value, onChange, options, placeholder = 'Select...', label, className }: MultiSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [customInput, setCustomInput] = useState('');
  const [showCustom, setShowCustom] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Close on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
        setShowCustom(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  // Focus search when opening
  useEffect(() => {
    if (open) {
      setTimeout(() => searchInputRef.current?.focus(), 50);
    }
  }, [open]);

  const toggle = (val: string) => {
    if (value.includes(val)) {
      onChange(value.filter((v) => v !== val));
    } else {
      onChange([...value, val]);
    }
  };

  const remove = (val: string) => {
    onChange(value.filter((v) => v !== val));
  };

  const addCustom = () => {
    const trimmed = customInput.trim().toLowerCase();
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed]);
    }
    setCustomInput('');
    setShowCustom(false);
  };

  const handleCustomKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addCustom();
    }
  };

  // Group and filter options
  const filtered = options.filter((o) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return o.label.toLowerCase().includes(s) || o.value.toLowerCase().includes(s) || o.category.toLowerCase().includes(s);
  });

  const grouped = new Map<string, SelectOption[]>();
  for (const o of filtered) {
    const g = grouped.get(o.category) || [];
    g.push(o);
    grouped.set(o.category, g);
  }

  // Check if search term doesn't match any existing option
  const noExactMatch = search.trim() && !options.some((o) => o.value.toLowerCase() === search.trim().toLowerCase());

  return (
    <div className={className} ref={containerRef}>
      {label && <p className="text-sm font-medium mb-2">{label}</p>}
      <div className="relative">
        {/* Trigger */}
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="flex w-full items-center justify-between rounded-md border bg-background px-3 py-2 text-sm min-h-[42px] hover:bg-muted/50 transition-colors"
        >
          <div className="flex flex-wrap gap-1 items-center flex-1">
            {value.length === 0 ? (
              <span className="text-muted-foreground">{placeholder}</span>
            ) : (
              value.map((tag) => {
                const opt = options.find((o) => o.value === tag);
                return (
                  <Badge key={tag} variant="secondary" className="gap-1 px-2 py-0.5 text-xs">
                    {opt?.label || tag}
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        remove(tag);
                      }}
                      className="ml-0.5 rounded-full hover:bg-muted-foreground/20 p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                );
              })
            )}
          </div>
          <ChevronDown className={`h-4 w-4 ml-2 shrink-0 text-muted-foreground transition-transform ${open ? 'rotate-180' : ''}`} />
        </button>

        {/* Dropdown */}
        {open && (
          <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md">
            {/* Search */}
            <div className="flex items-center border-b px-3 py-2">
              <Search className="h-4 w-4 text-muted-foreground mr-2" />
              <input
                ref={searchInputRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search genres..."
                className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
              />
            </div>

            {/* Options list */}
            <div className="max-h-[280px] overflow-y-auto p-1">
              {Array.from(grouped.entries()).map(([category, opts]) => (
                <div key={category}>
                  <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    {category}
                  </div>
                  {opts.map((opt) => {
                    const selected = value.includes(opt.value);
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => toggle(opt.value)}
                        className={`flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-left hover:bg-accent ${
                          selected ? 'bg-accent font-medium' : ''
                        }`}
                      >
                        <span className={`h-4 w-4 shrink-0 rounded border flex items-center justify-center ${
                          selected ? 'bg-primary border-primary' : 'border-muted-foreground/30'
                        }`}>
                          {selected && (
                            <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                              <path d="M2 5L4 7L8 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                          )}
                        </span>
                        <span>{opt.label}</span>
                      </button>
                    );
                  })}
                </div>
              ))}

              {filtered.length === 0 && !noExactMatch && (
                <p className="px-2 py-4 text-sm text-muted-foreground text-center">No matches found</p>
              )}
            </div>

            {/* "Other" custom input */}
            <div className="border-t p-2">
              {!showCustom ? (
                <button
                  type="button"
                  onClick={() => setShowCustom(true)}
                  className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-muted-foreground hover:bg-accent hover:text-foreground"
                >
                  <span className="text-base">+</span>
                  <span>Other — add your own</span>
                </button>
              ) : (
                <div className="flex gap-2">
                  <Input
                    value={customInput}
                    onChange={(e) => setCustomInput(e.target.value)}
                    onKeyDown={handleCustomKey}
                    placeholder="Type custom genre..."
                    className="h-8 text-sm"
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={addCustom}
                    disabled={!customInput.trim()}
                    className="shrink-0 rounded-md bg-primary px-3 py-1 text-xs text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                  >
                    Add
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      <p className="text-xs text-muted-foreground mt-1">Select from the list or add your own with "Other"</p>
    </div>
  );
}
