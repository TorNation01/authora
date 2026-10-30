import { api } from '@/lib/api';

export type FieldDef = {
  key: string;
  label: string;
  type: 'short' | 'text' | 'list' | 'rows' | 'checks';
  prompt: string;
  columns?: { key: string; label: string }[];
};

export type SectionDef = {
  key: string;
  number: number;
  title: string;
  intro: string;
  scope?: string;
  post_draft?: boolean;
  fields: FieldDef[];
};

export type SectionValues = Record<string, Record<string, unknown>>;

export type Completeness = {
  filled: number;
  total: number;
  pct: number;
  sections: Record<string, { title: string; filled: number; total: number; pct: number }>;
  missing: string[];
};

export type Saga = {
  id: string;
  name: string;
  version: number;
  updated_at: string | null;
  completeness: Completeness;
  projects?: SagaProject[];
  threads?: Record<string, number>;
  truths?: Record<string, number>;
};

export type SagaProject = {
  id: string;
  name: string;
  title: string;
  scope: string;
  book_count: number;
};

export type SeriesPlan = {
  id: string;
  name: string;
  kind: string;
  position: number;
  version: number;
  sections: SectionValues;
  section_status: Record<string, string>;
  completeness: Completeness;
};

export type Thread = {
  id: string;
  name: string;
  detail: string | null;
  status: string;
  opened_in: string | null;
  paid_in: string | null;
  notes: string | null;
  sort_order: number;
};

export type Truth = {
  id: string;
  statement: string;
  level: string;
  status: string;
  knows: string[];
  believes_otherwise: string[];
  reveal_point: string | null;
  notes: string | null;
  sort_order: number;
};

export type SagaSchema = {
  sections: SectionDef[];
  outline_sections: SectionDef[];
  series_sections: SectionDef[];
  connection_sections: SectionDef[];
  thread_statuses: string[];
  truth_statuses: string[];
  truth_levels: string[];
  scopes: string[];
};

export async function getSagaSchema(): Promise<SagaSchema> {
  return api<SagaSchema>('/api/v1/sagas/schema');
}

export async function listSagas(): Promise<{ sagas: Saga[]; count: number }> {
  return api('/api/v1/sagas');
}

export async function createSaga(name: string): Promise<{ saga: Saga }> {
  return api('/api/v1/sagas', { method: 'POST', body: JSON.stringify({ name }) });
}

export async function getSaga(id: string) {
  return api<{
    saga: Saga;
    sections: SectionValues;
    section_status: Record<string, string>;
    outline: { id: string; sections: SectionValues; version: number; completeness: Completeness };
    projects: SagaProject[];
    threads: Record<string, number>;
    truths: Record<string, number>;
  }>(`/api/v1/sagas/${id}`);
}

export async function updateSaga(
  id: string,
  payload: { name?: string; sections?: SectionValues; section_status?: Record<string, string> }
): Promise<{ saga: Saga; sections: SectionValues }> {
  return api(`/api/v1/sagas/${id}`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export async function updateSagaOutline(
  id: string,
  sections: SectionValues
): Promise<{ sections: SectionValues; version: number; completeness: Completeness }> {
  return api(`/api/v1/sagas/${id}/outline`, { method: 'PATCH', body: JSON.stringify({ sections }) });
}

export async function listSeries(id: string): Promise<{ series: SeriesPlan[] }> {
  return api(`/api/v1/sagas/${id}/series`);
}

export async function createSeries(id: string, name: string, kind = 'series'): Promise<SeriesPlan> {
  return api(`/api/v1/sagas/${id}/series`, { method: 'POST', body: JSON.stringify({ name, kind }) });
}

export async function updateSeries(
  sagaId: string,
  planId: string,
  payload: { name?: string; sections?: SectionValues; section_status?: Record<string, string> }
): Promise<SeriesPlan> {
  return api(`/api/v1/sagas/${sagaId}/series/${planId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteSeries(sagaId: string, planId: string): Promise<void> {
  return api(`/api/v1/sagas/${sagaId}/series/${planId}`, { method: 'DELETE' });
}

export async function listThreads(id: string): Promise<{ threads: Thread[]; counts: Record<string, number> }> {
  return api(`/api/v1/sagas/${id}/threads`);
}

export async function createThread(id: string, payload: Partial<Thread> & { name: string }) {
  return api<{ id: string }>(`/api/v1/sagas/${id}/threads`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateThread(sagaId: string, threadId: string, payload: Partial<Thread>) {
  return api<Thread>(`/api/v1/sagas/${sagaId}/threads/${threadId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteThread(sagaId: string, threadId: string): Promise<void> {
  return api(`/api/v1/sagas/${sagaId}/threads/${threadId}`, { method: 'DELETE' });
}

export async function listTruths(id: string): Promise<{ truths: Truth[]; counts: Record<string, number> }> {
  return api(`/api/v1/sagas/${id}/truths`);
}

export async function createTruth(id: string, payload: Partial<Truth> & { statement: string }) {
  return api<{ id: string }>(`/api/v1/sagas/${id}/truths`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateTruth(sagaId: string, truthId: string, payload: Partial<Truth>) {
  return api<Truth>(`/api/v1/sagas/${sagaId}/truths/${truthId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteTruth(sagaId: string, truthId: string): Promise<void> {
  return api(`/api/v1/sagas/${sagaId}/truths/${truthId}`, { method: 'DELETE' });
}

export async function linkProject(id: string, projectId: string) {
  return api(`/api/v1/sagas/${id}/projects`, {
    method: 'POST',
    body: JSON.stringify({ project_id: projectId }),
  });
}

export async function unlinkProject(id: string, projectId: string): Promise<void> {
  return api(`/api/v1/sagas/${id}/projects/${projectId}`, { method: 'DELETE' });
}

export async function listProjectsLite(): Promise<{ id: string; name: string }[]> {
  const res = await api<{ projects?: { id: string; name: string }[] } | { id: string; name: string }[]>(
    '/api/v1/projects'
  );
  if (Array.isArray(res)) return res;
  return res.projects || [];
}
