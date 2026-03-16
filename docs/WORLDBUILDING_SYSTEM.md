# Worldbuilding / Setting System

The AUTHORA Worldbuilding system stores world entries, locations, organisations, cultures, rules, and terminology for fiction and non-fiction.

## Overview

- **Project-scoped**: Locations belong to a project (optionally a book).
- **Hierarchical**: Parent-child for nested locations (e.g. city → district).
- **Flexible categories**: World, location, organisation, faction, culture, rule system, technology, magic, geography, environment, glossary, terminology.
- **Non-fiction adaptation**: Domain, framework, method, concept maps.

## Categories

| Category | Description |
|----------|-------------|
| `world` | Overall world |
| `location` | Physical place |
| `organisation` | Organisation |
| `faction` | Faction/group |
| `culture` | Culture |
| `rule_system` | Rules (magic, tech) |
| `technology` | Technology |
| `magic` | Magic system |
| `geography` | Geography |
| `environment` | Environment |
| `glossary` | Glossary term |
| `terminology` | Terminology |
| `domain` | Subject domain (non-fiction) |
| `framework` | Framework (non-fiction) |
| `method` | Method (non-fiction) |
| `concept` | Concept (non-fiction) |

## Fields

| Field | Description |
|-------|-------------|
| `name` | Name |
| `category` | Category |
| `description` | Description |
| `rules` | Rules (magic, tech) |
| `geography` | Geography |
| `environment` | Environment |
| `atmosphere` | Atmosphere |
| `history` | History |
| `constraints` | Constraints |

## API Endpoints

- `GET /api/v1/projects/{project_id}/vault/locations` — List (filter by `book_id`, `category`, `parent_id`)
- `POST /api/v1/projects/{project_id}/vault/locations` — Create
- `GET /api/v1/projects/{project_id}/vault/locations/{location_id}` — Get
- `PATCH /api/v1/projects/{project_id}/vault/locations/{location_id}` — Update
- `DELETE /api/v1/projects/{project_id}/vault/locations/{location_id}` — Delete

## Chapter Linking

- `POST /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/locations`

## Chapter Knowledge Panel

- `GET /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/knowledge`
