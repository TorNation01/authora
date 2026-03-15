'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { fetchConfig, getConfigSync, type AppConfig } from '@/lib/config';

const ConfigContext = createContext<AppConfig | null>(null);

export function ConfigProvider({ children }: { children: React.ReactNode }) {
  const [config, setConfig] = useState<AppConfig | null>(null);

  useEffect(() => {
    fetchConfig().then(setConfig);
  }, []);

  const value = config ?? getConfigSync();
  return <ConfigContext.Provider value={value}>{children}</ConfigContext.Provider>;
}

export function useConfig(): AppConfig {
  const ctx = useContext(ConfigContext);
  return ctx ?? getConfigSync();
}
