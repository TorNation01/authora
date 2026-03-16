/**
 * Polished user-facing copy for AUTHORA's research vault, idea capture,
 * character bible, worldbuilding, timeline, themes, and source manager.
 *
 * Tone: premium, clear, inspiring, supportive, intelligent.
 * Not academic unless needed. Not childish.
 */

// --- Vault page ---

export const VAULT_PAGE = {
  title: (projectName: string) => `${projectName} · Vault`,
  titleFallback: 'Vault',
  description:
    'Everything related to your book lives here. Ideas, characters, worldbuilding, research, and sources.',
} as const;

// --- Idea capture ---

export const IDEA_CAPTURE = {
  tagline: 'Capture it before it disappears.',
  saveTheSpark: 'Save the spark.',
  storeNowShapeLater: 'Store now, shape later.',
  placeholder: 'Capture an idea… (Enter to save)',
  addIdea: 'Add idea',
  moveToManuscript: 'Move to manuscript later',
  keepItClose: 'Keep it close.',
  captured: 'Idea captured',
  addIdeaTitle: 'Add idea',
  ideaTitlePlaceholder: 'Idea title',
  contentOptional: 'Content (optional)',
  moreDetails: 'More details…',
} as const;

// --- Ideas tab ---

export const IDEAS_TAB = {
  emptyTitle: 'No ideas yet',
  emptyDescription:
    'Capture ideas above or add structured idea cards. Store now, shape later—everything you capture stays here.',
  addIdea: 'Add idea',
} as const;

// --- Research vault ---

export const RESEARCH_VAULT = {
  tagline: 'Keep your supporting material in reach.',
  description:
    'Store notes, references, questions, and discoveries in one place. Research that stays connected to the writing.',
  emptyTitle: 'No research yet',
  emptyDescription:
    'Add research notes, clipped snippets, and summaries. Link them to chapters when you write—keep your supporting material in reach.',
  addResearch: 'Add research',
} as const;

// --- Character bible ---

export const CHARACTER_BIBLE = {
  tagline: 'Build people worth following.',
  description:
    'Keep character details consistent. Track motivations, history, and change across the manuscript.',
  emptyTitle: 'No characters yet',
  emptyDescription:
    'Add your first character to build your character bible. Track roles, arcs, and motivations—build people worth following.',
  addCharacter: 'Add character',
  addCharacterTitle: 'Add character',
  namePlaceholder: 'Full name',
  rolePlaceholder: 'e.g. protagonist, antagonist',
} as const;

// --- Worldbuilding ---

export const WORLDBUILDING = {
  tagline: 'Shape the world behind the words.',
  description:
    'Build places, rules, systems, and histories that hold together. Keep the setting coherent as the story grows.',
  emptyTitle: 'No locations yet',
  emptyDescription:
    'Build your world. Add places, factions, cultures, and rules—shape the world behind the words.',
  addLocation: 'Add location',
  addLocationTitle: 'Add location',
  namePlaceholder: 'Place, faction, or concept',
} as const;

// --- Timeline ---

export const TIMELINE = {
  tagline: 'See the story in sequence.',
  description: 'Keep events aligned. Track what happened, when, and why it matters.',
  emptyTitle: 'No timeline events yet',
  emptyDescription:
    'Track story chronology, backstory, and key moments. See the story in sequence.',
  addEvent: 'Add event',
} as const;

// --- Themes ---

export const THEMES = {
  tagline: 'Follow the deeper thread.',
  description:
    'Track the ideas running underneath the story. See where meaning repeats, evolves, or fades.',
} as const;

// --- Source manager ---

export const SOURCE_MANAGER = {
  tagline: 'Keep sources organised.',
  description:
    'Track what supports each claim or section. Mark what is verified, uncertain, or still needs review.',
  emptyTitle: 'No sources yet',
  emptyDescription:
    'Add books, articles, and references. Track citations and link to chapters—keep sources organised.',
  addSource: 'Add source',
  addSourceTitle: 'Add source',
  titlePlaceholder: 'Book, article, or reference',
  authorPlaceholder: 'Author or source name',
} as const;

// --- Chapter-linked knowledge ---

export const CHAPTER_KNOWLEDGE = {
  tagline: 'Everything relevant to this chapter, in one place.',
  description: 'Keep context beside the page. Write with the right details within reach.',
  panelTitle: 'Chapter knowledge',
  openVault: 'Open vault',
  emptyMessage: 'No linked material yet.',
  addFromVault: 'Add from vault',
} as const;

// --- Search ---

export const VAULT_SEARCH = {
  placeholder: 'Search vault…',
} as const;
