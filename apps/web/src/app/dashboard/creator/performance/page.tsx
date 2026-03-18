'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';
import { Loader2, BookOpen, TrendingUp, Eye } from 'lucide-react';

type TemplateStat = {
  id: string;
  slug: string;
  name: string;
  views: number;
  projects_count: number;
  books_count: number;
  sales_count: number;
  revenue_cents: number;
};

type PerformanceData = {
  templates: TemplateStat[];
  total_projects: number;
  total_books: number;
  total_sales: number;
  total_revenue_cents: number;
  total_views: number;
};

export default function CreatorPerformancePage() {
  const [data, setData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<PerformanceData>('/api/v1/creators/performance')
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Performance</h1>
        <p className="text-muted-foreground">Unable to load performance data.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Performance</h1>
        <p className="text-muted-foreground mt-1">
          Usage stats for your approved templates: projects and books created.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.total_views ?? 0}</div>
            <p className="text-xs text-muted-foreground">
              Template preview views
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total projects</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.total_projects}</div>
            <p className="text-xs text-muted-foreground">
              Projects started with your templates
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total books</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.total_books}</div>
            <p className="text-xs text-muted-foreground">
              Books created with your templates
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Sales</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.total_sales ?? 0}</div>
            <p className="text-xs text-muted-foreground">
              Templates sold
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${((data.total_revenue_cents ?? 0) / 100).toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">
              Total earnings
            </p>
          </CardContent>
        </Card>
      </div>

      {data.templates.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">
              No approved templates yet. Submit templates and get them approved to see usage here.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>By template</CardTitle>
            <p className="text-sm text-muted-foreground">
              Usage breakdown per approved template
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.templates.map((t) => (
                <div
                  key={t.id}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div>
                    <p className="font-medium">{t.name}</p>
                    <p className="text-sm text-muted-foreground">{t.slug}</p>
                  </div>
                  <div className="text-right">
                    {(t.views ?? 0) > 0 && (
                      <p className="text-sm text-muted-foreground">{t.views} views</p>
                    )}
                    <p className="font-medium">{t.projects_count} projects</p>
                    <p className="text-sm text-muted-foreground">{t.books_count} books</p>
                    {(t.sales_count ?? 0) > 0 && (
                      <p className="text-sm text-green-600">{t.sales_count} sales · ${((t.revenue_cents ?? 0) / 100).toFixed(2)}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
