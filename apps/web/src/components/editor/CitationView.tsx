'use client';

import { NodeViewWrapper } from '@tiptap/react';

export function CitationView({ node }: { node: { attrs: { sourceId: string; citationKey: string; preview: string } } }) {
  const { citationKey, preview } = node.attrs;
  const display = preview || citationKey || '[citation]';
  return (
    <NodeViewWrapper as="span" className="inline">
      <span
        data-citation
        className="rounded bg-primary/10 px-1.5 py-0.5 font-mono text-sm text-primary"
        style={{ cursor: 'default' }}
      >
        {display}
      </span>
    </NodeViewWrapper>
  );
}
