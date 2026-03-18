'use client';

import { Node, mergeAttributes } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import { CitationView } from './CitationView';

export interface CitationOptions {
  HTMLAttributes: Record<string, unknown>;
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    citation: {
      setCitation: (attrs: { sourceId: string; citationKey: string; preview?: string }) => ReturnType;
      unsetCitation: () => ReturnType;
    };
  }
}

export const Citation = Node.create<CitationOptions>({
  name: 'citation',

  group: 'inline',
  inline: true,
  atom: true,

  addAttributes() {
    return {
      sourceId: { default: null },
      citationKey: { default: '' },
      preview: { default: '' },
    };
  },

  parseHTML() {
    return [{ tag: 'span[data-citation]' }];
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', mergeAttributes({ 'data-citation': '' }, this.options.HTMLAttributes, HTMLAttributes), 0];
  },

  addNodeView() {
    return ReactNodeViewRenderer(CitationView);
  },

  addCommands() {
    return {
      setCitation:
        (attrs) =>
        ({ commands }) => {
          return commands.insertContent({ type: this.name, attrs });
        },
      unsetCitation:
        () =>
        ({ commands }) => {
          return commands.deleteSelection();
        },
    };
  },
});
