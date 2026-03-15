'use client';

import { useCallback, useRef, useState } from 'react';
import { api } from '@/lib/api';

const CACHE_TTL = 5 * 60 * 1000; // 5 min
const cache = new Map<string, { data: unknown; ts: number }>();

function getCached<T>(key: string): T | null {
  const entry = cache.get(key);
  if (!entry || Date.now() - entry.ts > CACHE_TTL) return null;
  return entry.data as T;
}

function setCache(key: string, data: unknown) {
  cache.set(key, { data, ts: Date.now() });
  if (cache.size > 500) {
    const oldest = [...cache.entries()].sort((a, b) => a[1].ts - b[1].ts)[0];
    if (oldest) cache.delete(oldest[0]);
  }
}

export interface LookupResult {
  word: string;
  definition: { phonetic?: string; meanings?: unknown[] } | null;
  synonyms: string[];
  antonyms: string[];
  phrase_alternatives: string[];
  simplification_hint: string | null;
  vocab_alternatives: string[];
  source: string;
}

export interface AnalyzeResult {
  repeated_phrases: { phrase: string; count: number }[];
  overused_words: { word: string; count: number }[];
  cliches: { phrase: string }[];
  readability_hints: { word: string; suggestion: string }[];
  vocab_enhancements: { word: string; alternatives: string[] }[];
}

export function useReference() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const lookup = useCallback(async (word: string): Promise<LookupResult | null> => {
    const key = word.trim().toLowerCase();
    if (!key) return null;
    const cached = getCached<LookupResult>(`lookup:${key}`);
    if (cached) return cached;

    abortRef.current?.abort();
    abortRef.current = new AbortController();
    setLoading(true);
    setError(null);
    try {
      const result = await api<LookupResult>(
        `/api/v1/reference/lookup?word=${encodeURIComponent(key)}`
      );
      setCache(`lookup:${key}`, result);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Lookup failed');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getSynonyms = useCallback(async (word: string): Promise<string[]> => {
    const key = word.trim().toLowerCase();
    if (!key) return [];
    const cached = getCached<{ synonyms: string[] }>(`syn:${key}`);
    if (cached) return cached.synonyms;

    try {
      const result = await api<{ synonyms: string[] }>(
        `/api/v1/reference/synonyms?word=${encodeURIComponent(key)}`
      );
      setCache(`syn:${key}`, result);
      return result.synonyms;
    } catch {
      return [];
    }
  }, []);

  const analyze = useCallback(async (text: string): Promise<AnalyzeResult | null> => {
    if (!text?.trim()) return null;
    const cached = getCached<AnalyzeResult>(`analyze:${text.slice(0, 500)}`);
    if (cached) return cached;

    setLoading(true);
    setError(null);
    try {
      const result = await api<AnalyzeResult>('/api/v1/reference/analyze', {
        method: 'POST',
        body: JSON.stringify({ text: text.slice(0, 50000) }),
      });
      setCache(`analyze:${text.slice(0, 500)}`, result);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { lookup, getSynonyms, analyze, loading, error };
}
