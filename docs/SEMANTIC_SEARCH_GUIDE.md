# Semantic Search Guide

Semantic search finds content by meaning, not just exact keywords.

## How It Works

1. Content (notes, chapters, outlines) is chunked and embedded
2. Your query is embedded with the same model
3. Cosine similarity ranks chunks by relevance
4. Results show source type, excerpt, and score

## Using Search

1. Open a project
2. Click **Search** or go to `/dashboard/projects/{id}/search`
3. Enter a natural-language query (e.g. "where does the protagonist confront the villain")
4. Results show matching passages with source labels

## Source Types

| Type | Description |
|------|-------------|
| note | Research notes, ideas |
| chapter | Chapter content |
| chapter_brief | Ghostwriter briefs |
| outline_chapter | Outline chapter titles/summaries |

## Reindexing

If you add or change content, click **Reindex project** to refresh the index. New content is not searchable until reindexed.

## Filters

- **book_id**: Limit to a single book
- **source_types**: Comma-separated (e.g. `note,chapter`)

API: `GET /api/v1/projects/{id}/rag/search?q=...&book_id=...&source_types=...`
