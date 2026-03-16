import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Typography from '@tiptap/extension-typography';
import Underline from '@tiptap/extension-underline';
import Highlight from '@tiptap/extension-highlight';

export const editorExtensions = (placeholder?: string) => [
  StarterKit.configure({
    heading: { levels: [1, 2, 3] },
    blockquote: {},
    bulletList: {},
    orderedList: {},
    listItem: {},
    codeBlock: false,
  }),
  Placeholder.configure({ placeholder: placeholder ?? 'Start where the words are ready.' }),
  Typography,
  Underline,
  Highlight.configure({ multicolor: true }),
];
