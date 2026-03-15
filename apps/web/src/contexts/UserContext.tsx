'use client';

import React, { createContext, useContext, useState } from 'react';

export interface UserInfo {
  id: string;
  email: string;
  display_name: string | null;
  is_admin: boolean;
}

const UserContext = createContext<UserInfo | null>(null);

export function UserProvider({
  children,
  user,
}: {
  children: React.ReactNode;
  user: UserInfo | null;
}) {
  return <UserContext.Provider value={user}>{children}</UserContext.Provider>;
}

export function useUser(): UserInfo | null {
  return useContext(UserContext);
}
