export const APP_NAME = 'AUTHORA';
export const APP_DESCRIPTION = 'AI-powered book builder and writing studio';

export const BOOK_TYPES = ['fiction', 'nonfiction'] as const;

export const FICTION_GENRES = [
  'Literary Fiction',
  'Science Fiction',
  'Fantasy',
  'Mystery',
  'Thriller',
  'Romance',
  'Historical Fiction',
  'Horror',
  'Young Adult',
  'Other',
] as const;

export const FICTION_TONES = [
  'Dark',
  'Hopeful',
  'Humorous',
  'Gritty',
  'Lyrical',
  'Suspenseful',
  'Whimsical',
  'Noir',
  'Epic',
  'Intimate',
] as const;

export const WORLD_CATEGORIES = [
  'Location',
  'Culture',
  'Magic',
  'Technology',
  'Religion',
  'Politics',
  'History',
  'Creatures',
  'Other',
] as const;

export const RELATIONSHIP_TYPES = [
  'Friend',
  'Enemy',
  'Mentor',
  'Rival',
  'Romantic',
  'Family',
  'Ally',
  'Antagonist',
  'Other',
] as const;

export const PLOT_STRUCTURES = ['three_act', 'hero_journey', 'save_the_cat', 'seven_point', 'custom'] as const;

export const EXPORT_FORMATS = ['docx', 'pdf', 'epub', 'txt'] as const;
export type ExportFormat = (typeof EXPORT_FORMATS)[number];
