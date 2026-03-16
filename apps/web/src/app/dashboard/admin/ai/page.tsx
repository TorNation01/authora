'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { Check, X, Loader2, RefreshCw, Server, Cloud } from 'lucide-react';

type Provider = {
  name: string;
  enabled: boolean;
  is_local: boolean;
  model_default: string;
};

type AIProvidersData = {
  providers: Provider[];
  provider_mode: string;
  ollama_enabled: boolean;
  ollama_base_url: string | null;
};

type OllamaModelsData = {
  models: Array<{ name: string; size?: number }>;
  base_url?: string;
  error?: string;
};

type OllamaHealthData = {
  ok: boolean;
  message: string;
};

export default function AdminAIPage() {
  const [data, setData] = useState<AIProvidersData | null>(null);
  const [ollamaModels, setOllamaModels] = useState<OllamaModelsData | null>(null);
  const [ollamaHealth, setOllamaHealth] = useState<OllamaHealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [providersRes, modelsRes, healthRes] = await Promise.all([
        api<AIProvidersData>('/api/v1/admin/ai/providers'),
        api<OllamaModelsData>('/api/v1/admin/ai/providers/ollama/models').catch(() => null),
        api<OllamaHealthData>('/api/v1/admin/ai/providers/ollama/health').catch(() => null),
      ]);
      setData(providersRes);
      setOllamaModels(modelsRes ?? null);
      setOllamaHealth(healthRes ?? null);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefreshModels = async () => {
    setRefreshing(true);
    try {
      const models = await api<OllamaModelsData>('/api/v1/admin/ai/providers/ollama/models');
      setOllamaModels(models);
      const health = await api<OllamaHealthData>('/api/v1/admin/ai/providers/ollama/health');
      setOllamaHealth(health);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">AI providers</h1>
        <p className="text-muted-foreground mt-1">
          Manage AI providers, check health, and refresh Ollama models.
        </p>
      </div>

      <Card variant="soft">
        <CardHeader>
          <CardTitle>Provider mode</CardTitle>
          <CardDescription>
            How AUTHORA chooses between local (Ollama) and cloud (OpenAI, Anthropic) providers.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-sm">
              {data?.provider_mode ?? 'auto'}
            </Badge>
            <span className="text-sm text-muted-foreground">
              {data?.provider_mode === 'auto' && 'Auto: prefer local, fallback to cloud'}
              {data?.provider_mode === 'cloud' && 'Cloud only: OpenAI or Anthropic'}
              {data?.provider_mode === 'local' && 'Local only: Ollama'}
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Change via AI_PROVIDER_MODE env (auto | cloud | local).
          </p>
        </CardContent>
      </Card>

      <Card variant="soft">
        <CardHeader>
          <CardTitle>Configured providers</CardTitle>
          <CardDescription>Providers available for AI tasks.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data?.providers?.map((p) => (
              <div
                key={p.name}
                className="flex items-center justify-between rounded-lg border p-4"
              >
                <div className="flex items-center gap-3">
                  {p.is_local ? (
                    <Server className="h-5 w-5 text-muted-foreground" />
                  ) : (
                    <Cloud className="h-5 w-5 text-muted-foreground" />
                  )}
                  <div>
                    <p className="font-medium capitalize">{p.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {p.is_local ? 'Local / self-hosted' : 'Cloud'} · Default: {p.model_default}
                    </p>
                  </div>
                </div>
                <Badge variant={p.enabled ? 'default' : 'secondary'}>
                  {p.enabled ? (
                    <>
                      <Check className="h-3 w-3 mr-1" />
                      Enabled
                    </>
                  ) : (
                    <>
                      <X className="h-3 w-3 mr-1" />
                      Disabled
                    </>
                  )}
                </Badge>
              </div>
            ))}
            {(!data?.providers?.length) && (
              <p className="text-muted-foreground">No AI providers configured.</p>
            )}
          </div>
        </CardContent>
      </Card>

      {data?.ollama_enabled && (
        <Card variant="soft">
          <CardHeader>
            <CardTitle>Ollama</CardTitle>
            <CardDescription>
              Local models at {data.ollama_base_url ?? 'http://localhost:11434'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Health</p>
                <p className="text-sm text-muted-foreground">
                  {ollamaHealth?.ok ? (
                    <span className="text-green-600 flex items-center gap-1">
                      <Check className="h-4 w-4" />
                      {ollamaHealth.message}
                    </span>
                  ) : (
                    <span className="text-destructive flex items-center gap-1">
                      <X className="h-4 w-4" />
                      {ollamaHealth?.message ?? 'Not reachable'}
                    </span>
                  )}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefreshModels}
                disabled={refreshing}
              >
                {refreshing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4 mr-1" />
                    Refresh models
                  </>
                )}
              </Button>
            </div>
            <div>
              <p className="font-medium mb-2">Available models</p>
              {ollamaModels?.error ? (
                <p className="text-sm text-destructive">{ollamaModels.error}</p>
              ) : ollamaModels?.models?.length ? (
                <ul className="text-sm space-y-1">
                  {ollamaModels.models.map((m) => (
                    <li key={m.name ?? ''} className="font-mono">
                      {m.name}
                      {m.size != null && m.size > 0 && (
                        <span className="text-muted-foreground ml-2">
                          ({(m.size / 1024 / 1024 / 1024).toFixed(2)} GB)
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No models found. Run <code className="rounded bg-muted px-1">ollama pull &lt;model&gt;</code> on the server.
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <Card variant="soft">
        <CardHeader>
          <CardTitle>Documentation</CardTitle>
          <CardDescription>Guides for AI configuration.</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="text-sm space-y-1 text-muted-foreground">
            <li>• AI_PROVIDER_MODES.md — Auto, Cloud, Local modes</li>
            <li>• OLLAMA_SETUP.md — Installing and configuring Ollama</li>
            <li>• MODEL_ROUTING.md — Task-based model selection</li>
            <li>• AI_ADMIN_GUIDE.md — Admin controls and health checks</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
