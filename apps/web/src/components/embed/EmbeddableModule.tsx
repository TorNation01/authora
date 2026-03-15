'use client';

import { useConfig } from '@/contexts/ConfigProvider';

/**
 * Embeddable module wrapper - renders children without full app shell.
 * Use when embedding AUTHORA in an iframe or parent Anakatech app.
 */
export function EmbeddableModule({ children }: { children: React.ReactNode }) {
  const config = useConfig();

  if (!config.feature_flags.embeddable_shell) {
    return <>{children}</>;
  }

  return (
    <div
      data-authora-embed="true"
      data-mode={config.deployment_mode}
      className="authora-embed min-h-screen"
    >
      {children}
    </div>
  );
}
