'use client';

import { useConfig } from '@/contexts/ConfigProvider';

/**
 * Embeddable module wrapper - renders children without full app shell.
 * Use when embedding AUTHORA in an iframe or parent Anakatech app.
 */
export function EmbeddableModule({ children }: { children: React.ReactNode }) {
  const config = useConfig();

  const useEmbeddable =
    config.feature_flags.embeddable_shell &&
    (config.is_anakatech || config.is_white_label) &&
    (config.integration_flags?.enable_shared_nav !== false);
  if (!useEmbeddable) {
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
