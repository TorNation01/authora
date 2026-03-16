'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Check, X, Loader2, RefreshCw, Server, Cloud, Save, ShieldCheck, Cpu } from 'lucide-react';

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
  ollama_hardware_tier?: string | null;
  ai_provider?: string;
  ai_model?: string;
  openai_configured?: boolean;
  anthropic_configured?: boolean;
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

type HardwareTierInfo = {
  id: string;
  label: string;
  description: string;
  source: string;
  detection_message?: string;
  ram_gb?: number;
  vram_gb?: number;
};

type ModelRolesData = {
  roles: string[];
  mappings: Record<string, { ollama: string; openai: string; anthropic: string }>;
  effective_mappings?: Record<string, { ollama: string; openai: string; anthropic: string }>;
  defaults: Record<string, string>;
  tier_recommended?: Record<string, string>;
  ollama_models: Array<{ name: string; size?: number }>;
  ollama_base_url: string | null;
  db_overrides: Record<string, string>;
  hardware_tier?: HardwareTierInfo;
  fallback_chains?: Record<string, string[]>;
  rag_limits?: Record<string, number>;
};

type ValidateResult = {
  valid: boolean;
  results: Record<string, { model: string; valid: boolean }>;
  available_count: number;
  message?: string;
};

const ROLE_LABELS: Record<string, string> = {
  quick_assist_model: 'Quick assist',
  default_writing_model: 'Default writing',
  premium_drafting_model: 'Premium drafting',
  fiction_ideation_model: 'Fiction ideation',
  nonfiction_structure_model: 'Nonfiction structure',
  editing_polish_model: 'Editing & polish',
  embeddings_model: 'Embeddings',
  optional_vision_model: 'Vision (optional)',
};

export default function AdminAIPage() {
  const { toast } = useToast();
  const [data, setData] = useState<AIProvidersData | null>(null);
  const [ollamaModels, setOllamaModels] = useState<OllamaModelsData | null>(null);
  const [ollamaHealth, setOllamaHealth] = useState<OllamaHealthData | null>(null);
  const [modelRoles, setModelRoles] = useState<ModelRolesData | null>(null);
  const [validateResult, setValidateResult] = useState<ValidateResult | null>(null);
  const [roleOverrides, setRoleOverrides] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [applying, setApplying] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);
  const [testingOllama, setTestingOllama] = useState(false);
  const [configForm, setConfigForm] = useState<{
    provider_mode: string;
    openai_api_key: string;
    anthropic_api_key: string;
    ollama_enabled: boolean;
    ollama_base_url: string;
    ollama_hardware_tier: string;
  }>({
    provider_mode: 'auto',
    openai_api_key: '',
    anthropic_api_key: '',
    ollama_enabled: false,
    ollama_base_url: 'http://localhost:11434',
    ollama_hardware_tier: '',
  });

  const fetchData = async () => {
    try {
      const [providersRes, modelsRes, healthRes, rolesRes] = await Promise.all([
        api<AIProvidersData>('/api/v1/admin/ai/providers'),
        api<OllamaModelsData>('/api/v1/admin/ai/providers/ollama/models').catch(() => null),
        api<OllamaHealthData>('/api/v1/admin/ai/providers/ollama/health').catch(() => null),
        api<ModelRolesData>('/api/v1/admin/ai/model-roles').catch(() => null),
      ]);
      setData(providersRes);
      setOllamaModels(modelsRes ?? null);
      setOllamaHealth(healthRes ?? null);
      setModelRoles(rolesRes ?? null);
      if (rolesRes?.mappings) {
        const overrides: Record<string, string> = {};
        for (const [role, m] of Object.entries(rolesRes.mappings)) {
          overrides[role] = (m as { ollama: string }).ollama;
        }
        setRoleOverrides(overrides);
      }
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (data) {
      setConfigForm((f) => ({
        ...f,
        provider_mode: data.provider_mode ?? 'auto',
        ollama_enabled: data.ollama_enabled ?? false,
        ollama_base_url: data.ollama_base_url ?? 'http://localhost:11434',
        ollama_hardware_tier: data.ollama_hardware_tier ?? '',
      }));
    }
  }, [data]);

  const handleRefreshModels = async () => {
    setRefreshing(true);
    try {
      const [models, health, roles] = await Promise.all([
        api<OllamaModelsData>('/api/v1/admin/ai/providers/ollama/models'),
        api<OllamaHealthData>('/api/v1/admin/ai/providers/ollama/health'),
        api<ModelRolesData>('/api/v1/admin/ai/model-roles'),
      ]);
      setOllamaModels(models);
      setOllamaHealth(health);
      setModelRoles(roles);
      if (roles?.mappings) {
        const overrides: Record<string, string> = {};
        for (const [role, m] of Object.entries(roles.mappings)) {
          overrides[role] = (m as { ollama: string }).ollama;
        }
        setRoleOverrides(overrides);
      }
    } finally {
      setRefreshing(false);
    }
  };

  const handleSaveRoles = async () => {
    setSaving(true);
    try {
      await api('/api/v1/admin/ai/model-roles', {
        method: 'PUT',
        body: JSON.stringify({ mappings: roleOverrides }),
      });
      await fetchData();
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async () => {
    setValidating(true);
    try {
      const res = await api<ValidateResult>('/api/v1/admin/ai/model-roles/validate');
      setValidateResult(res);
    } finally {
      setValidating(false);
    }
  };

  const handleApplyRecommended = async () => {
    setApplying(true);
    try {
      await api('/api/v1/admin/ai/model-roles/apply-recommended', { method: 'POST' });
      await fetchData();
    } finally {
      setApplying(false);
    }
  };

  const handleSaveConfig = async () => {
    setSavingConfig(true);
    try {
      const body: Record<string, unknown> = {
        ai_provider_mode: configForm.provider_mode,
        ollama_enabled: configForm.ollama_enabled,
        ollama_base_url: configForm.ollama_base_url || undefined,
      };
      if (configForm.openai_api_key) body.openai_api_key = configForm.openai_api_key;
      if (configForm.anthropic_api_key) body.anthropic_api_key = configForm.anthropic_api_key;
      if (configForm.ollama_hardware_tier) body.ollama_hardware_tier = configForm.ollama_hardware_tier;
      await api('/api/v1/admin/ai/config', { method: 'PUT', body: JSON.stringify(body) });
      toast({ title: 'AI config saved', description: 'Restart the API for changes to take effect.' });
      await fetchData();
    } catch {
      toast({ title: 'Failed to save', variant: 'destructive' });
    } finally {
      setSavingConfig(false);
    }
  };

  const handleTestOllama = async () => {
    setTestingOllama(true);
    try {
      const res = await api<{ ok: boolean; message: string }>('/api/v1/admin/ai/providers/ollama/test', {
        method: 'POST',
        body: JSON.stringify({ base_url: configForm.ollama_base_url || 'http://localhost:11434' }),
      });
      if (res.ok) {
        toast({ title: 'Ollama connection OK' });
      } else {
        toast({ title: 'Ollama connection failed', description: res.message, variant: 'destructive' });
      }
    } catch (e) {
      toast({ title: 'Test failed', description: e instanceof Error ? e.message : 'Unknown error', variant: 'destructive' });
    } finally {
      setTestingOllama(false);
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
          <CardTitle>AI provider configuration</CardTitle>
          <CardDescription>
            Add or update AI providers, API keys, and Ollama settings. Restart the API after saving.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label>Provider mode</Label>
            <Select
              value={configForm.provider_mode}
              onValueChange={(v) => setConfigForm((f) => ({ ...f, provider_mode: v }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto: prefer local, fallback to cloud</SelectItem>
                <SelectItem value="cloud">Cloud only: OpenAI or Anthropic</SelectItem>
                <SelectItem value="local">Local only: Ollama</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-4 border-t pt-4">
            <p className="text-sm font-medium">Cloud providers (API keys)</p>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="openai_key">OpenAI API key</Label>
                <Input
                  id="openai_key"
                  type="password"
                  placeholder={data?.openai_configured ? '•••••••• (leave blank to keep)' : 'sk-...'}
                  value={configForm.openai_api_key}
                  onChange={(e) => setConfigForm((f) => ({ ...f, openai_api_key: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="anthropic_key">Anthropic API key</Label>
                <Input
                  id="anthropic_key"
                  type="password"
                  placeholder={data?.anthropic_configured ? '•••••••• (leave blank to keep)' : 'sk-ant-...'}
                  value={configForm.anthropic_api_key}
                  onChange={(e) => setConfigForm((f) => ({ ...f, anthropic_api_key: e.target.value }))}
                />
              </div>
            </div>
          </div>
          <div className="space-y-4 border-t pt-4">
            <p className="text-sm font-medium">Ollama (local)</p>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={configForm.ollama_enabled}
                onChange={(e) => setConfigForm((f) => ({ ...f, ollama_enabled: e.target.checked }))}
                className="rounded border-input"
              />
              <span className="text-sm">Enable Ollama</span>
            </label>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="ollama_base_url">Base URL</Label>
                <Input
                  id="ollama_base_url"
                  value={configForm.ollama_base_url}
                  onChange={(e) => setConfigForm((f) => ({ ...f, ollama_base_url: e.target.value }))}
                  placeholder="http://localhost:11434"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="ollama_tier">Hardware tier (1–4)</Label>
                <Select
                  value={configForm.ollama_hardware_tier || 'auto'}
                  onValueChange={(v) => setConfigForm((f) => ({ ...f, ollama_hardware_tier: v === 'auto' ? '' : v }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Auto-detect" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">Auto-detect</SelectItem>
                    <SelectItem value="1">1 — Light</SelectItem>
                    <SelectItem value="2">2 — Balanced</SelectItem>
                    <SelectItem value="3">3 — Strong</SelectItem>
                    <SelectItem value="4">4 — Premium</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleTestOllama}
                disabled={testingOllama}
              >
                {testingOllama ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                Test Ollama connection
              </Button>
              <Button size="sm" onClick={handleSaveConfig} disabled={savingConfig}>
                {savingConfig ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4 mr-1" />}
                Save config
              </Button>
            </div>
          </div>
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

      {data?.ollama_enabled && modelRoles && (
        <Card variant="soft">
          <CardHeader>
            <CardTitle>Model role mapping</CardTitle>
            <CardDescription>
              Assign Ollama models to tasks. Hardware tier determines recommended defaults. Overrides apply globally.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {modelRoles.hardware_tier && (
              <div className="rounded-lg border p-3 flex items-start gap-3">
                <Cpu className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="font-medium">Hardware tier: {modelRoles.hardware_tier.label}</p>
                  <p className="text-sm text-muted-foreground">{modelRoles.hardware_tier.description}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {modelRoles.hardware_tier.detection_message}
                    {modelRoles.hardware_tier.ram_gb != null && ` · ${modelRoles.hardware_tier.ram_gb} GB RAM`}
                    {modelRoles.hardware_tier.vram_gb != null && ` · ${modelRoles.hardware_tier.vram_gb} GB VRAM`}
                  </p>
                </div>
              </div>
            )}
            <div className="flex items-center gap-2 flex-wrap">
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
              <Button
                variant="outline"
                size="sm"
                onClick={handleValidate}
                disabled={validating}
              >
                {validating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <ShieldCheck className="h-4 w-4 mr-1" />
                    Validate
                  </>
                )}
              </Button>
              <Button size="sm" onClick={handleSaveRoles} disabled={saving}>
                {saving ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-1" />
                    Save
                  </>
                )}
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleApplyRecommended}
                disabled={applying}
              >
                {applying ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Cpu className="h-4 w-4 mr-1" />
                    Apply recommended
                  </>
                )}
              </Button>
            </div>
            {validateResult && (
              <div className="rounded-lg border p-3 text-sm">
                <p className="font-medium mb-1">
                  Validation: {validateResult.valid ? (
                    <span className="text-green-600 flex items-center gap-1">
                      <Check className="h-4 w-4" />
                      All models valid
                    </span>
                  ) : (
                    <span className="text-amber-600 flex items-center gap-1">
                      <X className="h-4 w-4" />
                      Some models not found
                    </span>
                  )}
                </p>
                {validateResult.message && (
                  <p className="text-muted-foreground">{validateResult.message}</p>
                )}
                <p className="text-muted-foreground mt-1">
                  {validateResult.available_count} models available at {modelRoles.ollama_base_url ?? 'Ollama'}
                </p>
              </div>
            )}
            <div className="grid gap-4 sm:grid-cols-2">
              {modelRoles.roles.map((role) => (
                <div key={role} className="space-y-2">
                  <Label className="text-sm font-medium">
                    {ROLE_LABELS[role] ?? role}
                  </Label>
                  <Select
                    value={roleOverrides[role] ?? modelRoles.mappings[role]?.ollama ?? modelRoles.defaults[role] ?? ''}
                    onValueChange={(v) => setRoleOverrides((prev) => ({ ...prev, [role]: v }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select model" />
                    </SelectTrigger>
                    <SelectContent>
                      {modelRoles.ollama_models.map((m) => (
                        <SelectItem key={m.name} value={m.name}>
                          {m.name}
                        </SelectItem>
                      ))}
                      {(() => {
                        const current = roleOverrides[role] ?? modelRoles.mappings[role]?.ollama ?? modelRoles.defaults[role] ?? '';
                        if (current && !modelRoles.ollama_models.some((m) => m.name === current)) {
                          return (
                            <SelectItem key={current} value={current}>
                              {current} (custom)
                            </SelectItem>
                          );
                        }
                        return null;
                      })()}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    Recommended: {modelRoles.tier_recommended?.[role] ?? modelRoles.defaults[role] ?? '—'}
                  </p>
                  {modelRoles.effective_mappings?.[role]?.ollama !== modelRoles.mappings[role]?.ollama && (
                    <p className="text-xs text-amber-600">
                      Fallback: {modelRoles.effective_mappings?.[role]?.ollama}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card variant="soft">
        <CardHeader>
          <CardTitle>Ollama</CardTitle>
          <CardDescription>
            {data?.ollama_enabled
              ? `Local models at ${data.ollama_base_url ?? 'http://localhost:11434'}`
              : 'Enable Ollama in the configuration above to use local models.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {data?.ollama_enabled ? (
            <>
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
            </>
          ) : (
            <p className="text-sm text-muted-foreground">
              Enable Ollama in the AI provider configuration above, then save to use local models.
            </p>
          )}
        </CardContent>
      </Card>

      <Card variant="soft">
        <CardHeader>
          <CardTitle>Embeddings & RAG</CardTitle>
          <CardDescription>
            Semantic search and retrieval-augmented generation. Requires embeddings provider (Ollama).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Enable via EMBEDDINGS_ENABLED=true and OLLAMA_EMBEDDING_MODEL=nomic-embed-text. See docs:
            OLLAMA_EMBEDDINGS_SETUP.md, RAG_ARCHITECTURE.md.
          </p>
        </CardContent>
      </Card>

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
            <li>• OLLAMA_MODEL_ROLE_MAP.md — Role definitions and default mappings</li>
            <li>• OLLAMA_HARDWARE_TIERS.md — Hardware tier definitions and mappings</li>
            <li>• AI_HARDWARE_AUTOMAP.md — Auto-selection and fallback behavior</li>
            <li>• SERVER_SIZING_AND_MODEL_SELECTION.md — Server sizing guidance</li>
            <li>• OLLAMA_PERFORMANCE_TUNING.md — Performance tuning</li>
            <li>• AI_MODEL_REGISTRY.md — Registry design and usage</li>
            <li>• ADMIN_AI_MODEL_SETTINGS.md — Model role mapping UI and API</li>
            <li>• AI_ADMIN_GUIDE.md — Admin controls and health checks</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
