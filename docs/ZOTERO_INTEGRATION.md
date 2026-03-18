# Zotero Integration

AUTHORA integrates with [Zotero](https://www.zotero.org/) to sync reference libraries for academic and professional writing.

## Overview

- **Connect** a Zotero user or group library via API key
- **Sync** items into project vault sources
- **Map** Zotero metadata to CSL JSON for citation generation
- **Reconnect** flow when API key expires or library access changes

## Architecture

### Components

| Component | Purpose |
|----------|---------|
| `ZoteroConnection` | User's Zotero API key, library type (user/group), library ID |
| `Source` (vault) | Synced items with `zotero_item_key`, `zotero_connection_id`, `csl_json` |
| `zotero_service` | Sync logic, Zotero API calls via pyzotero |

### API Endpoints

- `GET /api/v1/projects/{id}/references/zotero/connections` — List connections
- `POST /api/v1/projects/{id}/references/zotero/connections` — Connect (verifies key)
- `POST /api/v1/projects/{id}/references/zotero/connections/{conn_id}/sync` — Sync to project
- `DELETE /api/v1/projects/{id}/references/zotero/connections/{conn_id}` — Disconnect

## Setup

### 1. Zotero API Key

1. Go to [Zotero Settings → Feeds/API](https://www.zotero.org/settings/keys)
2. Create a new private key
3. Enable **Library access** (read) and optionally **Write access** (for future write support)

### 2. Library ID

- **User library**: Your user ID is in the URL when viewing your library: `https://www.zotero.org/users/123456`
- **Group library**: Group ID is in the URL: `https://www.zotero.org/groups/789012`

### 3. Connect in AUTHORA

1. Open project → Settings or Vault → References
2. Add Zotero connection: library type, library ID, API key
3. Connection is verified before saving
4. Run sync to import items into vault sources

## Sync Behavior

- **Full sync**: All top-level items from the library are synced
- **Mapping**: Zotero item types → vault `source_type` (book, article, website, document, etc.)
- **CSL JSON**: Stored in `Source.csl_json` for citation generation
- **Updates**: Re-running sync updates existing sources by `zotero_item_key`

## Failure Handling

- **Verify on connect**: API key is tested before saving
- **Sync errors**: Stored in `ZoteroConnection.sync_error`; `sync_status` = `error`
- **Reconnect**: User can delete connection and re-add with a new key
- **Metadata validation**: Sources can be marked `needs_review` for manual review

## Standalone Mode

AUTHORA works without Zotero. Users can:

- Add sources manually via Vault → Sources
- Use citation placeholders and resolve later
- Generate bibliographies from manually entered sources

## References

- [Zotero Web API](https://www.zotero.org/support/dev/web_api/v3/start)
- [pyzotero](https://github.com/urschrei/pyzotero) — Python Zotero API client
