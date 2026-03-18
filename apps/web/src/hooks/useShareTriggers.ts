'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export type ShareTriggerSuggestion = {
  trigger_type: string;
  message: string;
  share_type: string;
};

export function useShareTriggers() {
  const [suggestions, setSuggestions] = useState<ShareTriggerSuggestion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<{ suggestions: ShareTriggerSuggestion[] }>('/api/v1/growth/share-triggers')
      .then((res) => setSuggestions(res.suggestions || []))
      .catch(() => setSuggestions([]))
      .finally(() => setLoading(false));
  }, []);

  const markShown = async (triggerType: string) => {
    try {
      await api(`/api/v1/growth/share-triggers/${encodeURIComponent(triggerType)}/shown`, {
        method: 'POST',
      });
      setSuggestions((prev) => prev.filter((s) => s.trigger_type !== triggerType));
    } catch {
      // Ignore
    }
  };

  return { suggestions, loading, markShown };
}
