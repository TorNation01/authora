'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PageHeader } from '@/components/layout/PageHeader';

export default function AdminOnboardingPage() {
  return (
    <div className="p-6 lg:p-8 max-w-4xl">
      <PageHeader
        title="Onboarding"
        description="Configure onboarding flow, defaults, and experiment readiness"
      />

      <div className="space-y-6">
          <Card variant="soft">
            <CardHeader>
              <CardTitle>Onboarding configuration</CardTitle>
              <CardDescription>
                Default settings and feature flags for the onboarding experience. Changes here affect new users and
                returning users who have not completed setup.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium mb-1">Default guidance modes</p>
                <p className="text-sm text-muted-foreground">
                  Guided, Flexible, Freeform — all enabled by default. Users choose during onboarding and project
                  creation.
                </p>
              </div>
              <div>
                <p className="text-sm font-medium mb-1">Default accountability presets</p>
                <p className="text-sm text-muted-foreground">
                  None, Gentle, Structured, Buddy — mapped to accountability settings on completion.
                </p>
              </div>
              <div>
                <p className="text-sm font-medium mb-1">Onboarding steps</p>
                <p className="text-sm text-muted-foreground">
                  Welcome → Writer type → Book type → Guidance → Work style → Pace → Complete. All steps enabled.
                </p>
              </div>
              <div>
                <p className="text-sm font-medium mb-1">First-book journey</p>
                <p className="text-sm text-muted-foreground">
                  Guided path from idea to export. Phases: Define → Structure → Opening → Moving → Midpoint → Finish →
                  Revise → Export.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card variant="soft">
            <CardHeader>
              <CardTitle>Experiment readiness</CardTitle>
              <CardDescription>
                Architecture supports A/B testing and plan-based onboarding variants. Enable via feature flags when
                ready.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Onboarding variants by plan (e.g. starter vs pro flow)</li>
                <li>Step enable/disable per variant</li>
                <li>Default templates and guidance modes per plan</li>
                <li>Drop-off tracking (via analytics integration)</li>
              </ul>
            </CardContent>
          </Card>
        </div>
    </div>
  );
}
