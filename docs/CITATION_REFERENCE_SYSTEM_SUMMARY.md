# Citation & Reference System — Production-Ready Summary

## 1. Zotero Integration Summary

- **Connect**: Users add Zotero API key, library type (user/group), library ID
- **Verify**: Connection is tested before saving; invalid keys are rejected
- **Sync**: Full sync imports Zotero items into project vault sources
- **Mapping**: Zotero metadata → vault Source + CSL JSON for citation
- **Reconnect**: Delete connection and re-add with new key on failure
- **Standalone**: AUTHORA works without Zotero; manual source entry supported

**API**: `GET/POST/DELETE /api/v1/projects/{id}/references/zotero/connections`, `POST .../sync`

---

## 2. Citation/Style Support Summary

- **CSL-based**: Real citation generation via citeproc-py (no placeholders)
- **Styles**: APA, MLA, Chicago, Harvard, IEEE, MHRA (built-in)
- **Custom**: Add styles to `citation_styles` table or `authora/data/csl/`
- **Project-level**: Set style per project or per book
- **Preview**: Citation preview before insertion
- **Bibliography**: Generate formatted bibliography from sources

**API**: `GET/PUT /api/v1/projects/{id}/references/styles/project`, `POST .../citation-preview`, `POST .../bibliography`

---

## 3. Bibliography System Summary

- **Real generation**: citeproc-py processes CSL styles
- **Input**: Source IDs (from vault, manual or Zotero)
- **Output**: Formatted bibliography entries (plain or HTML)
- **Flow**: Select sources → choose style → receive formatted list

**API**: `POST /api/v1/projects/{id}/references/bibliography`

---

## 4. Editor Citation Workflow Summary

- **TipTap Citation node**: Inline citation marker with `sourceId`, `citationKey`, `preview`
- **Insert**: `editor.commands.setCitation({ sourceId, citationKey, preview })`
- **Display**: Renders as styled span (e.g. `(Author, 2024)` or `[1]`)
- **Chapter citations**: `ChapterCitation` links source to chapter for bibliography
- **Placeholder flow**: Citation placeholders can be resolved to sources

---

## 5. Production-Ready Confirmation

| Requirement | Status |
|-------------|--------|
| Zotero integration | ✅ pyzotero, verify, sync, reconnect |
| Source library sync | ✅ Zotero → vault sources |
| Bibliography manager | ✅ Vault sources + bibliography API |
| Citation insertion | ✅ TipTap Citation node + chapter citations |
| Citation style support | ✅ CSL, multiple styles |
| CSL-based formatting | ✅ citeproc-py |
| Reference notes | ✅ SourceNote model + API |
| Source organization | ✅ Vault sources, tags, status |
| Project-linked references | ✅ Sources per project, ChapterSourceLink, ChapterCitation |
| Academic workflows | ✅ Essay, literature review, annotated bib support |
| Manual source entry | ✅ Vault sources without Zotero |
| No fake citations | ✅ Real CSL processing |
| Documentation | ✅ ZOTERO_INTEGRATION, CITATION_SYSTEM, CSL_STYLE_SUPPORT, REFERENCE_MANAGER, BIBLIOGRAPHY_GENERATION |

**The citation/reference system is production-ready.**
