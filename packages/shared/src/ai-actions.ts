/** AI writing assistant - shared types and constants */

export const AI_MODES = [
  { id: 'assist', label: 'Assist', description: 'Light suggestions, preserve your voice' },
  { id: 'co_write', label: 'Co-Write', description: 'Collaborative, moderate changes' },
  { id: 'ghostwriter', label: 'Ghostwriter', description: 'Full generation from your brief' },
  { id: 'editing', label: 'Edit', description: 'Improve existing text, minimal creativity' },
  { id: 'spark', label: 'Spark', description: 'Creative brainstorming' },
] as const;

export const ASSISTANCE_LEVELS = [
  { id: 'strict', label: 'Strict', description: 'Minimal changes' },
  { id: 'moderate', label: 'Moderate', description: 'Balanced' },
  { id: 'creative', label: 'Creative', description: 'More freedom' },
] as const;

export type AIModeId = (typeof AI_MODES)[number]['id'];
export type AssistanceLevelId = (typeof ASSISTANCE_LEVELS)[number]['id'];

export interface AIAction {
  id: string;
  label: string;
  description: string;
  uses_selection: boolean;
  uses_context: boolean;
}

export interface AIActionRequest {
  action_id: string;
  book_id: string;
  chapter_id?: string;
  selection?: string;
  context?: string;
  mode?: AIModeId;
  level?: AssistanceLevelId;
  book_type?: 'fiction' | 'nonfiction' | 'general';
  extra?: Record<string, string>;
}
