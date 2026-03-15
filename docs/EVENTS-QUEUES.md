# Events & Queues

## Event Catalog

| Event | Payload | Emitted By | Consumers |
|-------|---------|------------|-----------|
| `user.registered` | `{ user_id }` | auth | notifications, billing |
| `user.logged_in` | `{ user_id, ip }` | auth | audit |
| `book.created` | `{ book_id, project_id, user_id }` | projects | - |
| `chapter.created` | `{ chapter_id, book_id }` | chapters | - |
| `chapter.updated` | `{ chapter_id, word_delta }` | chapters | insights, gamification |
| `document.saved` | `{ document_id, user_id }` | documents | insights |
| `goal.created` | `{ goal_id, deadline }` | goals | reminders |
| `goal.completed` | `{ goal_id, user_id }` | goals | gamification |
| `export.requested` | `{ export_job_id }` | export | worker |
| `export.completed` | `{ export_job_id, url }` | worker | notifications |


## Queue Definitions

### export.jobs
- **Purpose**: Async export generation
- **Producer**: API (POST /export/books/:id)
- **Consumer**: worker
- **Payload**: `{ job_id, book_id, format, user_id }`
- **Retries**: 3
- **DLQ**: export.jobs.dlq

### ai.batch
- **Purpose**: Batch AI completion
- **Producer**: API or scheduled
- **Consumer**: worker
- **Payload**: `{ request_id, prompt, context }`
- **Retries**: 2

### notifications.send
- **Purpose**: Send email/push/in-app
- **Producer**: Event handlers
- **Consumer**: worker
- **Payload**: `{ channel, user_id, template, data }`
- **Retries**: 5

### insights.analyze
- **Purpose**: Writing analysis
- **Producer**: Document save handler
- **Consumer**: worker
- **Payload**: `{ document_id }`
- **Retries**: 2

### gamification.sync
- **Purpose**: Recalculate streaks/achievements
- **Producer**: Cron, chapter.updated
- **Consumer**: worker
- **Payload**: `{ user_id }`
- **Retries**: 2

### reminders.trigger
- **Purpose**: Dispatch goal reminders
- **Producer**: Cron (every 15 min)
- **Consumer**: worker
- **Payload**: `{ reminder_id }`
- **Retries**: 1


## Redis Streams / BullMQ Structure

```
authora:queue:export
authora:queue:ai
authora:queue:notifications
authora:queue:insights
authora:queue:gamification
authora:queue:reminders
```

## Event Bus (Internal)

For standalone/SaaS, use in-process event bus + queue dispatch:

```python
# Pseudocode
async def on_chapter_updated(event):
    await queue.enqueue("insights.analyze", {"document_id": event.document_id})
    await queue.enqueue("gamification.sync", {"user_id": event.user_id})
```
