/** Domain event types for AUTHORA */

export type DomainEventType =
  | 'user.registered'
  | 'user.logged_in'
  | 'book.created'
  | 'chapter.updated'
  | 'document.saved'
  | 'goal.created'
  | 'goal.completed'
  | 'export.requested'
  | 'export.completed';

export interface DomainEvent<T = unknown> {
  id: string;
  type: DomainEventType;
  source: string;
  timestamp: string;
  user_id?: string;
  tenant_id?: string;
  payload: T;
  metadata?: Record<string, unknown>;
}
