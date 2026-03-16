# AUTHORA Research Vault — Implementation Summary

## 1. Research Vault Summary

The Research Vault (`vault_research_entries`) stores project research: notes, clipped snippets, summaries, documents, topic folders, and fact-check entries. Entries support `topic`, `tags`, `needs_verification`, `source_id` linking, and hierarchical `parent_id` for folders. Research can be linked to chapters for the knowledge panel.

**API**: `GET/POST /api/v1/projects/{project_id}/vault/research`

---

## 2. Idea Capture Summary

The Idea Capture system (`vault_ideas`) supports quick notes, idea cards, scene/chapter/title ideas, plot twists, dialogue snippets, thematic notes, and save-for-later. Status workflow: raw_idea → maybe_later → planned → used → archived. Ideas can be pinned, starred, tagged, and linked to project, book, chapter, character, location, and timeline event.

**API**: `GET/POST /api/v1/projects/{project_id}/vault/ideas`

---

## 3. Character Bible Summary

The Character Bible (`vault_characters`) stores full profiles: full_name, aliases, role_in_story, archetype, age, appearance_notes, voice_notes, personality_traits, goals, fears, motivations, internal/external conflict, backstory, timeline_notes, secrets, quirks, dialogue_patterns, emotional_arc, private_notes, status (active/background/archived). Characters link to chapters via `chapter_character_links`.

**API**: `GET/POST /api/v1/projects/{project_id}/vault/characters`

---

## 4. Worldbuilding / Setting Summary

The Worldbuilding system (`vault_locations`) stores world entries, locations, organisations, factions, cultures, rules, geography, environment, atmosphere, history, and constraints. Categories include location, world, organisation, culture, magic, technology, glossary, terminology, and non-fiction variants (domain, framework, method, concept). Supports parent-child hierarchy.

**API**: `GET/POST /api/v1/projects/{project_id}/vault/locations`

---

## 5. Timeline / Source Manager Summary

**Timeline** (`vault_timeline_events`): Event cards with title, description, event_type (story_event, chapter_event, backstory, life_event, memoir_stage, historical_reference), event_date, date_label, sequence_order, storyline, time_period. Linked to chapters via `chapter_event_links`.

**Source Manager** (`vault_sources`): Title, author, source_type (book, article, website, interview, etc.), publication_date, url, usage_notes, topic_tags, quote_extracts, citation_notes, reliability_note, status (verified/unverified/needs_review). Linked to chapters via `chapter_source_links`.

**API**: `GET/POST /api/v1/projects/{project_id}/vault/timeline`, `GET/POST .../vault/sources`

---

## 6. Chapter-Linked Knowledge Summary

The Chapter Knowledge Panel aggregates all linked material for a chapter: characters, locations, events, themes, sources, research. Endpoint: `GET /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/knowledge`. Attach endpoints: `POST .../chapters/{chapter_id}/characters`, `.../locations`, `.../events`, `.../themes`, `.../sources`, `.../research`.

---

## 7. Production-Ready Confirmation

The AUTHORA research and knowledge system is **production-ready**:

- **Models**: Idea, ResearchEntry, VaultCharacter, VaultLocation, TimelineEvent, VaultRelationship, Theme, Source, and chapter-link tables
- **Migration**: `031_add_vault_tables.py` applied
- **API**: Full CRUD for all vault entities, chapter linking, knowledge panel, vault search
- **AI retrieval**: `GET /api/v1/projects/{project_id}/vault/search` for text search across vault entities
- **Admin**: `GET/PUT /api/v1/admin/vault-config` for feature availability, entry limits, AI retrieval, export, attachments
- **Documentation**: RESEARCH_VAULT.md, IDEA_CAPTURE_SYSTEM.md, CHARACTER_BIBLE.md, WORLDBUILDING_SYSTEM.md, TIMELINE_AND_EVENT_TRACKER.md, SOURCE_MANAGER.md, CHAPTER_LINKED_KNOWLEDGE.md, THEMES_AND_MOTIFS.md
- **Standalone & server-hosted**: Project-scoped design works for both modes
- **Fiction & non-fiction**: Categories and fields adapt to memoir, workbook, ghostwriting
