'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { cn } from '@/lib/utils';

const LAYOUT_STORAGE_KEY = 'authora-manuscript-layout';

export interface PanelLayout {
  rightPanelWidth: number; // 0 = collapsed, 280-600 = width in px
  rightPanelMode: 'ai' | 'notes' | 'reference' | 'revision' | 'progress';
}

const DEFAULT_LAYOUT: PanelLayout = {
  rightPanelWidth: 360,
  rightPanelMode: 'notes',
};

function loadLayout(bookId: string): PanelLayout {
  if (typeof window === 'undefined') return DEFAULT_LAYOUT;
  try {
    const raw = localStorage.getItem(`${LAYOUT_STORAGE_KEY}-${bookId}`);
    if (!raw) return DEFAULT_LAYOUT;
    const parsed = JSON.parse(raw) as Partial<PanelLayout>;
    return {
      rightPanelWidth: typeof parsed.rightPanelWidth === 'number' ? Math.min(600, Math.max(0, parsed.rightPanelWidth)) : DEFAULT_LAYOUT.rightPanelWidth,
      rightPanelMode: parsed.rightPanelMode ?? DEFAULT_LAYOUT.rightPanelMode,
    };
  } catch {
    return DEFAULT_LAYOUT;
  }
}

function saveLayout(bookId: string, layout: PanelLayout) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(`${LAYOUT_STORAGE_KEY}-${bookId}`, JSON.stringify(layout));
  } catch {
    // ignore
  }
}

interface ResizablePanelLayoutProps {
  bookId: string;
  main: React.ReactNode;
  rightPanel: React.ReactNode | null;
  rightPanelMode?: PanelLayout['rightPanelMode'];
  className?: string;
}

export function ResizablePanelLayout({
  bookId,
  main,
  rightPanel,
  rightPanelMode,
  className,
}: ResizablePanelLayoutProps) {
  const [layout, setLayout] = useState<PanelLayout>(() => loadLayout(bookId));
  const [isDragging, setIsDragging] = useState(false);
  const [localWidth, setLocalWidth] = useState(layout.rightPanelWidth);
  const dragWidthRef = useRef(layout.rightPanelWidth);

  useEffect(() => {
    if (rightPanelMode != null) {
      setLayout((prev) => ({ ...prev, rightPanelMode }));
    }
  }, [rightPanelMode]);

  useEffect(() => {
    saveLayout(bookId, layout);
  }, [bookId, layout]);

  const showPanel = rightPanel && layout.rightPanelWidth > 0;
  const displayWidth = isDragging ? localWidth : layout.rightPanelWidth;

  useEffect(() => {
    setLocalWidth(layout.rightPanelWidth);
  }, [layout.rightPanelWidth]);

  const handleDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  useEffect(() => {
    if (!isDragging) return;
    const onMove = (e: MouseEvent) => {
      const vw = window.innerWidth;
      const minW = 240;
      const maxW = Math.min(600, vw * 0.5);
      let w = vw - e.clientX;
      w = Math.max(minW, Math.min(maxW, w));
      dragWidthRef.current = w;
      setLocalWidth(w);
    };
    const onUp = () => {
      setIsDragging(false);
      setLayout((prev) => ({ ...prev, rightPanelWidth: dragWidthRef.current }));
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
  }, [isDragging]);

  return (
    <div className={cn('flex flex-1 min-h-0', className)}>
      <div className="flex-1 min-w-0 overflow-hidden">{main}</div>
      {showPanel && (
        <>
          <div
            role="separator"
            aria-orientation="vertical"
            className={cn(
              'w-1 flex-shrink-0 cursor-col-resize hover:bg-primary/20 transition-colors',
              isDragging && 'bg-primary/30'
            )}
            onMouseDown={handleDragStart}
            style={{ minWidth: 4 }}
          />
          <div
            className="flex-shrink-0 overflow-hidden border-l bg-card flex flex-col"
            style={{ width: displayWidth }}
          >
            {rightPanel}
          </div>
        </>
      )}
    </div>
  );
}
