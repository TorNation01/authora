/**
 * AUTHORA runtime config - deployment mode, feature flags, branding.
 * Fetched from API at bootstrap; falls back to env for SSR/build.
 */

export type DeploymentMode = 'standalone' | 'anakatech' | 'white_label';
export type AppMode = DeploymentMode;

export interface IntegrationFlags {
  enable_sso: boolean;
  enable_shared_nav: boolean;
  enable_shared_notifications: boolean;
  enable_shared_analytics: boolean;
  enable_shared_billing: boolean;
  enable_brand_overrides: boolean;
}

export interface FeatureFlags {
  standalone_auth: boolean;
  standalone_landing: boolean;
  standalone_setup_wizard: boolean;
  local_admin_creation: boolean;
  sso_ready: boolean;
  embeddable_shell: boolean;
  shared_notifications: boolean;
  shared_workspace_identity: boolean;
  tenant_aware: boolean;
  billing: boolean;
}

export interface BrandingConfig {
  product_name: string;
  tagline: string;
  logo_url: string | null;
  favicon_url: string | null;
  primary_color: string | null;
  show_powered_by: boolean;
}

export interface AppConfig {
  deployment_mode: DeploymentMode;
  app_mode?: AppMode;
  is_standalone: boolean;
  is_anakatech: boolean;
  is_white_label?: boolean;
  feature_flags: FeatureFlags;
  integration_flags?: IntegrationFlags;
  branding: BrandingConfig;
}

const DEFAULT_INTEGRATION_FLAGS: IntegrationFlags = {
  enable_sso: false,
  enable_shared_nav: false,
  enable_shared_notifications: false,
  enable_shared_analytics: false,
  enable_shared_billing: false,
  enable_brand_overrides: true,
};

const DEFAULT: AppConfig = {
  deployment_mode: 'standalone',
  app_mode: 'standalone',
  is_standalone: true,
  is_anakatech: false,
  is_white_label: false,
  feature_flags: {
    standalone_auth: true,
    standalone_landing: true,
    standalone_setup_wizard: true,
    local_admin_creation: true,
    sso_ready: false,
    embeddable_shell: false,
    shared_notifications: false,
    shared_workspace_identity: false,
    tenant_aware: false,
    billing: false,
  },
  integration_flags: DEFAULT_INTEGRATION_FLAGS,
  branding: {
    product_name: 'AUTHORA',
    tagline: 'AI-Powered Book Builder',
    logo_url: null,
    favicon_url: null,
    primary_color: null,
    show_powered_by: true,
  },
};

let cachedConfig: AppConfig | null = null;

export async function fetchConfig(): Promise<AppConfig> {
  if (cachedConfig) return cachedConfig;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
  const base = typeof window !== 'undefined' ? '' : apiUrl;
  try {
    const res = await fetch(`${base}/api/v1/config`);
    if (res.ok) {
      const data = await res.json();
      cachedConfig = {
        deployment_mode: data.deployment_mode || 'standalone',
        app_mode: data.app_mode || data.deployment_mode || 'standalone',
        is_standalone: data.is_standalone ?? true,
        is_anakatech: data.is_anakatech ?? false,
        is_white_label: data.is_white_label ?? false,
        feature_flags: { ...DEFAULT.feature_flags, ...data.feature_flags },
        integration_flags: { ...DEFAULT_INTEGRATION_FLAGS, ...data.integration_flags },
        branding: { ...DEFAULT.branding, ...data.branding },
      };
      return cachedConfig;
    }
  } catch {
    // Fallback to env or defaults
  }
  const mode = (process.env.NEXT_PUBLIC_DEPLOYMENT_MODE as DeploymentMode) || (process.env.NEXT_PUBLIC_APP_MODE as AppMode) || 'standalone';
  cachedConfig = {
    ...DEFAULT,
    deployment_mode: mode,
    app_mode: mode,
    is_standalone: mode === 'standalone',
    is_anakatech: mode === 'anakatech',
    is_white_label: mode === 'white_label',
  };
  return cachedConfig;
}

export function getConfigSync(): AppConfig {
  if (cachedConfig) return cachedConfig;
  const mode = (process.env.NEXT_PUBLIC_DEPLOYMENT_MODE as DeploymentMode) || (process.env.NEXT_PUBLIC_APP_MODE as AppMode) || 'standalone';
  return {
    ...DEFAULT,
    deployment_mode: mode,
    app_mode: mode,
    is_standalone: mode === 'standalone',
    is_anakatech: mode === 'anakatech',
    is_white_label: mode === 'white_label',
  };
}

export function clearConfigCache(): void {
  cachedConfig = null;
}
