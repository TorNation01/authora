'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Share2 } from 'lucide-react';
import { ShareDialog } from './ShareDialog';
import type { ShareType } from './ShareDialog';

interface ShareTriggerProps {
  shareType: ShareType;
  payload: Record<string, unknown>;
  displayName?: string;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  className?: string;
  children?: React.ReactNode;
}

export function ShareTrigger({
  shareType,
  payload,
  displayName,
  variant = 'ghost',
  size = 'sm',
  className,
  children,
}: ShareTriggerProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        variant={variant}
        size={size}
        className={className}
        onClick={() => setOpen(true)}
      >
        <Share2 className="h-4 w-4" />
        {children ?? (size !== 'icon' && <span className="ml-1.5">Share</span>)}
      </Button>
      <ShareDialog
        open={open}
        onOpenChange={setOpen}
        shareType={shareType}
        payload={payload}
        displayName={displayName}
      />
    </>
  );
}
