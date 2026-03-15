'use client';

import { useState, useEffect } from 'react';
import { useReference } from './useReference';
import type { LookupResult, AnalyzeResult } from './useReference';

export function useReferencePanelData(lookupWord: string | null | undefined, documentText: string | undefined) {
  const { lookup, analyze, loading, error } = useReference();
  const [lookupResult, setLookupResult] = useState<LookupResult | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResult | null>(null);

  useEffect(() => {
    if (lookupWord) {
      lookup(lookupWord).then(setLookupResult);
    } else {
      setLookupResult(null);
    }
  }, [lookupWord, lookup]);

  useEffect(() => {
    if (documentText) {
      analyze(documentText).then(setAnalysisResult);
    } else {
      setAnalysisResult(null);
    }
  }, [documentText, analyze]);

  return { lookupResult, analysisResult, loading, error };
}
