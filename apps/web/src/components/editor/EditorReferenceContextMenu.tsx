'use client';

import { useCallback, useEffect, useState } from 'react';
import { BookOpen } from 'lucide-react';

interface EditorReferenceContextMenuProps {
  children: React.ReactNode;
  selection: string;
  onLookup: (word: string) => void;
}

export function EditorReferenceContextMenu({
  children,
  selection,
  onLookup,
}: EditorReferenceContextMenuProps) {
  const [menu, setMenu] = useState<{ x: number; y: number; word: string } | null>(null);

  const handleContextMenu = useCallback(
    (e: React.MouseEvent) => {
      const text = selection.trim();
      const words = text.split(/\s+/);
      if (words.length === 1 && /^[a-zA-Z']+$/.test(words[0])) {
        e.preventDefault();
        setMenu({ x: e.clientX, y: e.clientY, word: words[0] });
      }
    },
    [selection]
  );

  useEffect(() => {
    if (!menu) return;
    const close = () => setMenu(null);
    window.addEventListener('click', close);
    window.addEventListener('scroll', close, true);
    return () => {
      window.removeEventListener('click', close);
      window.removeEventListener('scroll', close, true);
    };
  }, [menu]);

  return (
    <>
      <div onContextMenu={handleContextMenu} className="contents">
        {children}
      </div>
      {menu && (
        <div
          className="fixed z-50 min-w-[140px] rounded-lg border bg-popover py-1 shadow-md"
          style={{ left: menu.x, top: menu.y }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            type="button"
            className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-accent"
            onClick={() => {
              onLookup(menu.word);
              setMenu(null);
            }}
          >
            <BookOpen className="h-4 w-4" />
            Look up &quot;{menu.word}&quot;
          </button>
        </div>
      )}
    </>
  );
}
