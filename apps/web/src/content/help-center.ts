/**
 * Help center content - organized by topic for the in-app help center.
 * Designed to reduce overwhelm: short, scannable, actionable.
 */

export interface HelpArticle {
  id: string;
  title: string;
  summary: string;
  body: string[];
  tags: string[];
}

export const HELP_ARTICLES: HelpArticle[] = [
  // Fiction
  {
    id: 'fiction-getting-started',
    title: 'Writing fiction in AUTHORA',
    summary: 'Set up your novel with genre templates, outline, and chapter briefs.',
    body: [
      'Choose a fiction template (romance, thriller, fantasy, mystery) when creating your book. Each template includes setup questions and suggested structure.',
      'Build your outline in the manuscript sidebar. Add chapters and short summaries. You can reorder anytime.',
      'Add a chapter brief for each chapter—a few sentences about what happens. The AI uses briefs to generate drafts.',
      'Write in the editor or use Ghostwriter mode to generate a draft from your outline and brief.',
    ],
    tags: ['fiction', 'getting-started', 'outline'],
  },
  {
    id: 'fiction-plot-structure',
    title: 'Plot structure for fiction',
    summary: 'Use the three-act structure, hero\'s journey, or your own framework.',
    body: [
      'AUTHORA doesn\'t force a structure. Use the outline to organize your story however you like.',
      'For three-act: add Part 1, Part 2, Part 3 as sections, then chapters under each.',
      'For hero\'s journey: create chapters for each stage (Ordinary World, Call to Adventure, etc.).',
      'Link notes to chapters for character arcs, subplots, and world-building details.',
    ],
    tags: ['fiction', 'structure', 'outline'],
  },
  {
    id: 'fiction-ghostwriter',
    title: 'Ghostwriter mode for fiction',
    summary: 'Generate chapter drafts from your outline and briefs.',
    body: [
      'Ghostwriter mode uses your outline and chapter briefs to draft full chapters.',
      'Choose Light (suggestions only), Heavy (full drafts), or Full (AI handles most drafting).',
      'You can edit, approve, or reject. Your voice stays in control—AI assists.',
      'Best for: getting unstuck, first drafts, exploring alternate directions.',
    ],
    tags: ['fiction', 'ai', 'ghostwriter'],
  },

  // Non-fiction
  {
    id: 'nonfiction-getting-started',
    title: 'Writing non-fiction in AUTHORA',
    summary: 'Structure your book with parts, chapters, and research notes.',
    body: [
      'Choose a non-fiction template (memoir, business, self-help, how-to) when creating your book.',
      'Non-fiction templates include setup questions for audience, angle, and key takeaways.',
      'Use the outline for parts and chapters. Add summaries that capture the main point of each section.',
      'Link research notes to chapters. Keep sources, quotes, and data in the Notes panel.',
    ],
    tags: ['non-fiction', 'getting-started', 'outline'],
  },
  {
    id: 'nonfiction-structure',
    title: 'Structuring non-fiction',
    summary: 'Organize your book for clarity and flow.',
    body: [
      'Start with your core message. Each part and chapter should support it.',
      'Use the outline to map: introduction → main content → conclusion.',
      'Chapter summaries help you stay on track. Update them as you write.',
      'Reference panel: look up definitions, synonyms, readability. Select text to analyze.',
    ],
    tags: ['non-fiction', 'structure'],
  },

  // AI
  {
    id: 'ai-overview',
    title: 'AI support without overwhelm',
    summary: 'AI assists when you need it. You stay in control.',
    body: [
      'AUTHORA\'s AI helps you write faster without replacing your voice. It can suggest, expand, rewrite, or draft—you choose when and how much.',
      'Select text and use the AI menu: rewrite, expand, shorten, change tone, or continue writing.',
      'You can set your preferred AI level: minimal (suggestions only), moderate (rewrites and expansions), or full (drafts and continuations).',
      'Your text is sent to the AI provider only when you trigger an action. We do not train models on your content.',
    ],
    tags: ['ai', 'overview'],
  },
  {
    id: 'ai-actions',
    title: 'AI actions in the editor',
    summary: 'Rewrite, expand, shorten, and more—select text to get started.',
    body: [
      'Select text in the editor. The AI bubble menu appears with actions.',
      'Rewrite: change style or tone. Expand: add detail. Shorten: condense. Improve: fix clarity and flow.',
      'Continue: AI writes from your cursor or selection. Use when you\'re stuck.',
      'Fix grammar: corrects errors without changing your voice.',
    ],
    tags: ['ai', 'editor'],
  },
  {
    id: 'ai-api-key',
    title: 'AI API key setup',
    summary: 'Add your own API key for AI features.',
    body: [
      'Go to Settings → AI to add your OpenAI or Anthropic API key.',
      'Keys are stored securely and never shared. Your content is sent only when you use AI features.',
      'Without a key, some AI actions may be limited. Check your plan for included usage.',
    ],
    tags: ['ai', 'settings'],
  },

  // Accountability
  {
    id: 'accountability-overview',
    title: 'Staying on track—without guilt',
    summary: 'Set goals, get supportive nudges, and track progress.',
    body: [
      'Set a pace you can actually keep. Progress builds books. Small, steady sessions count.',
      'Choose your style: Gentle (soft nudges), Balanced (regular check-ins), or Structured (clear expectations).',
      'We send supportive nudges when you\'ve been away. Your book is still waiting for you.',
      'Track progress on the Progress page. Streaks, milestones, and word counts—progress deserves to be seen.',
    ],
    tags: ['accountability', 'goals'],
  },
  {
    id: 'accountability-goals',
    title: 'Setting word goals',
    summary: 'Daily or weekly targets that work for you.',
    body: [
      'Go to Home → Progress to set your goal.',
      'Daily: e.g. 500 words/day. Weekly: e.g. 3,500 words/week.',
      'We count words from your manuscript. Notes and outlines don\'t count.',
      'Adjust anytime. Consistency matters more than intensity—we\'ll help you get back on track.',
    ],
    tags: ['accountability', 'goals'],
  },

  // Export
  {
    id: 'export-overview',
    title: 'Exporting your manuscript',
    summary: 'DOCX, PDF, EPUB, and plain text—one click.',
    body: [
      'Go to Dashboard → Export. Choose format: DOCX, PDF, EPUB, or TXT.',
      'Select which chapters to include. Export full manuscript or a subset.',
      'DOCX: best for editing in Word, querying agents. PDF: for beta readers, print.',
      'EPUB: for e-readers and self-publishing. TXT: plain text, no formatting.',
    ],
    tags: ['export'],
  },
  {
    id: 'export-formats',
    title: 'Export format guide',
    summary: 'When to use each format.',
    body: [
      'DOCX: Industry standard. Use for agent queries, editing, collaboration.',
      'PDF: Read-only. Good for beta readers, proofreading, print preview.',
      'EPUB: E-book format. Use for Kindle, Kobo, Apple Books, self-publishing.',
      'TXT: Plain text. Minimal formatting. Good for backups or conversion.',
    ],
    tags: ['export', 'formats'],
  },

  // Publishing prep
  {
    id: 'publishing-prep',
    title: 'Publishing prep tools',
    summary: 'Synopsis, blurb, and query materials.',
    body: [
      'AUTHORA helps you create materials for querying agents or self-publishing.',
      'Synopsis: Generate a 1–2 page summary of your book from your manuscript.',
      'Blurb: Back-cover copy. Short, punchy, hooks the reader.',
      'Query letter: Draft a query from your synopsis and blurb. Customize before sending.',
    ],
    tags: ['publishing', 'synopsis', 'blurb'],
  },

  // Story Integrity
  {
    id: 'story-integrity',
    title: 'Story Integrity Engine',
    summary: 'Find unresolved threads, weak arcs, and structural gaps.',
    body: [
      'The Story Integrity Engine finds what your story is missing—unresolved plot threads, weak character arcs, and structural gaps.',
      'Open the Story Health panel from the toolbar. Click Scan to analyze your manuscript.',
      'Review issues one at a time. Resolve or mark as intentional. The engine adapts to fiction, non-fiction, memoir, and workbook.',
    ],
    tags: ['integrity', 'story', 'plot', 'structure'],
  },

  // Story Density
  {
    id: 'story-density',
    title: 'Story Density Engine',
    summary: 'Cut filler, find repetition, strengthen weak sections.',
    body: [
      'The Story Density Engine finds filler, repetition, and weak sections. It helps you tighten prose without losing what matters.',
      'Use it during revision—after you have a full draft. Trim redundant content, expand thin transitions.',
      'Open Story Health → Density tab. Run a scan to see what to cut, compress, or strengthen.',
    ],
    tags: ['density', 'filler', 'repetition', 'revision'],
  },

  // General
  {
    id: 'first-steps',
    title: 'Your first steps',
    summary: 'Get started in a few minutes.',
    body: [
      '1. Create a project. Name it (e.g. "My Novel" or "Business Book").',
      '2. Add a book. Choose a template or start from scratch.',
      '3. Add chapters to your outline. One sentence per chapter is enough to start.',
      '4. Open a chapter and start writing. Or use Ghostwriter to generate a draft.',
      '5. Set a word goal in Progress if you\'d like supportive nudges.',
    ],
    tags: ['getting-started'],
  },
  {
    id: 'all-in-one',
    title: 'All your tools in one place',
    summary: 'Outline, notes, editor, export—no tab chaos.',
    body: [
      'Outline: In the manuscript sidebar. Add, reorder, and summarize chapters.',
      'Notes: Research, ideas, character sheets. Link to chapters for easy reference.',
      'Reference: Definitions, synonyms, readability. Select text to analyze.',
      'Version history: See previous versions. Restore if you want to go back.',
      'Export: One click to DOCX, PDF, EPUB, or TXT.',
    ],
    tags: ['overview'],
  },
];

/** Maps in-app article IDs to public help page slugs for "Read full guide" links. */
export const ARTICLE_TO_HELP_SLUG: Record<string, string> = {
  'first-steps': 'getting-started',
  'fiction-getting-started': 'getting-started',
  'nonfiction-getting-started': 'getting-started',
  'fiction-plot-structure': 'writing-with-authora',
  'nonfiction-structure': 'writing-with-authora',
  'all-in-one': 'writing-with-authora',
  'story-integrity': 'story-integrity-engine',
  'story-density': 'story-density-engine',
  'ai-overview': 'ai-assistance',
  'ai-actions': 'ai-assistance',
  'fiction-ghostwriter': 'ai-assistance',
  'ai-api-key': 'account-and-billing',
  'accountability-overview': 'account-and-billing',
  'accountability-goals': 'account-and-billing',
  'export-overview': 'export-and-publishing',
  'export-formats': 'export-and-publishing',
  'publishing-prep': 'export-and-publishing',
};

export const HELP_CATEGORIES = [
  { id: 'getting-started', label: 'Getting started', icon: '🚀' },
  { id: 'fiction', label: 'Fiction writing', icon: '📖' },
  { id: 'non-fiction', label: 'Non-fiction writing', icon: '📚' },
  { id: 'ai', label: 'AI features', icon: '✨' },
  { id: 'accountability', label: 'Staying on track', icon: '🎯' },
  { id: 'export', label: 'Exporting', icon: '📤' },
  { id: 'publishing', label: 'Publishing prep', icon: '📝' },
  { id: 'integrity', label: 'Story Integrity', icon: '🔍' },
  { id: 'density', label: 'Story Density', icon: '📊' },
] as const;

export function getArticlesByTag(tag: string): HelpArticle[] {
  return HELP_ARTICLES.filter((a) => a.tags.includes(tag));
}

export function getArticle(id: string): HelpArticle | undefined {
  return HELP_ARTICLES.find((a) => a.id === id);
}

export function searchArticles(query: string): HelpArticle[] {
  const q = query.toLowerCase().trim();
  if (!q) return HELP_ARTICLES;
  return HELP_ARTICLES.filter(
    (a) =>
      a.title.toLowerCase().includes(q) ||
      a.summary.toLowerCase().includes(q) ||
      a.tags.some((t) => t.includes(q)) ||
      a.body.some((p) => p.toLowerCase().includes(q))
  );
}
