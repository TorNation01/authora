'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Loader2, BookOpen, Star, Copy, Plus } from 'lucide-react';
import Link from 'next/link';

type Template = {
  id: string;
  slug: string;
  category: string;
  parent_id: string | null;
  name: string;
  description: string | null;
  book_type: string | null;
  genre: string | null;
  structure_framework: string | null;
  sort_order: number;
  is_featured: boolean;
  is_disabled: boolean;
  access_level: string;
  premium_pack_slug: string | null;
  price_cents: number | null;
  is_paid: boolean;
  creator_id: string | null;
};

export default function AdminTemplatesPage() {
  const { toast } = useToast();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [includeDisabled, setIncludeDisabled] = useState(false);
  const [updating, setUpdating] = useState<Record<string, boolean>>({});

  const fetchTemplates = () => {
    setLoading(true);
    api<{ templates: Template[] }>(`/api/v1/admin/templates?include_disabled=${includeDisabled}`)
      .then((res) => setTemplates(res.templates))
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTemplates();
  }, [includeDisabled]);

  const handleToggle = async (id: string, field: 'is_featured' | 'is_disabled', value: boolean) => {
    setUpdating((p) => ({ ...p, [id]: true }));
    try {
      await api(`/api/v1/admin/templates/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ [field]: value }),
      });
      toast({ title: 'Updated', description: `${field} set to ${value}` });
      fetchTemplates();
    } catch {
      toast({ title: 'Failed to update', variant: 'destructive' });
    } finally {
      setUpdating((p) => ({ ...p, [id]: false }));
    }
  };

  const handleDuplicate = async (id: string) => {
    setUpdating((p) => ({ ...p, [id]: true }));
    try {
      const res = await api<{ id: string; slug: string; name: string }>(`/api/v1/admin/templates/${id}/duplicate`, {
        method: 'POST',
      });
      toast({ title: 'Template duplicated', description: `Created "${res.name}"` });
      fetchTemplates();
    } catch {
      toast({ title: 'Failed to duplicate', variant: 'destructive' });
    } finally {
      setUpdating((p) => ({ ...p, [id]: false }));
    }
  };

  const byCategory = templates.reduce<Record<string, Template[]>>((acc, t) => {
    (acc[t.category] = acc[t.category] || []).push(t);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Project templates</h1>
          <p className="text-muted-foreground mt-1">
            Manage templates: visibility, featured, access level, pricing.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <Switch checked={includeDisabled} onCheckedChange={setIncludeDisabled} />
            Include disabled
          </label>
          <Button variant="outline" asChild>
            <Link href="/dashboard/templates">
              <BookOpen className="h-4 w-4 mr-2" />
              View marketplace
            </Link>
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(byCategory).map(([category, items]) => (
            <Card key={category} variant="soft">
              <CardHeader className="pb-2">
                <h2 className="text-lg font-semibold">{category}</h2>
                <p className="text-sm text-muted-foreground">{items.length} templates</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {items.map((t) => (
                    <div
                      key={t.id}
                      className={`flex items-center justify-between rounded-lg border p-3 ${t.is_disabled ? 'opacity-60' : ''}`}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <BookOpen className="h-4 w-4 text-muted-foreground shrink-0" />
                        <div className="min-w-0">
                          <p className="font-medium truncate">{t.name}</p>
                          <p className="text-xs text-muted-foreground truncate">{t.slug}</p>
                        </div>
                        <div className="flex flex-wrap gap-1 shrink-0">
                          {t.is_featured && (
                            <Badge variant="default" className="text-xs">
                              <Star className="h-3 w-3 mr-0.5" />
                              Featured
                            </Badge>
                          )}
                          {t.access_level !== 'free' && (
                            <Badge variant="outline" className="text-xs">
                              {t.access_level}
                            </Badge>
                          )}
                          {t.is_disabled && (
                            <Badge variant="secondary" className="text-xs">
                              Disabled
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-4 shrink-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">Featured</span>
                          <Switch
                            checked={t.is_featured}
                            onCheckedChange={(v) => handleToggle(t.id, 'is_featured', v)}
                            disabled={updating[t.id]}
                          />
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">Disabled</span>
                          <Switch
                            checked={t.is_disabled}
                            onCheckedChange={(v) => handleToggle(t.id, 'is_disabled', v)}
                            disabled={updating[t.id]}
                          />
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDuplicate(t.id)}
                          disabled={updating[t.id]}
                        >
                          {updating[t.id] ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card variant="soft">
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            To create a new template from scratch, use the duplicate button and edit the copy. Full template creation
            API: <code className="rounded bg-muted px-1">POST /api/v1/admin/templates</code>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
