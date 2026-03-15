export type BookType = 'fiction' | 'nonfiction';

export interface FictionPlannerData {
  genre?: string;
  subgenre?: string;
  premise?: string;
  characters?: Array<{ name: string; role: string; description?: string }>;
  plotPoints?: string[];
  worldbuilding?: Record<string, string>;
  targetWordCount?: number;
}

export interface NonfictionPlannerData {
  topic?: string;
  audience?: string;
  structure?: string[];
  keyPoints?: string[];
  targetWordCount?: number;
}

export type PlannerData = FictionPlannerData | NonfictionPlannerData;

export interface Chapter {
  id: string;
  bookId: string;
  title: string;
  sortOrder: number;
  content: Record<string, unknown>;
  wordCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface Book {
  id: string;
  projectId: string;
  title: string;
  genre?: string;
  type: BookType;
  plannerData?: PlannerData;
  createdAt: string;
  updatedAt: string;
}

export interface Project {
  id: string;
  userId: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

export interface User {
  id: string;
  email: string;
  displayName?: string;
  createdAt: string;
}

export interface Achievement {
  id: string;
  type: string;
  name: string;
  description: string;
  icon?: string;
  earnedAt?: string;
}
