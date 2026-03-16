# Front and Back Matter

Structured front and back matter blocks for exportable manuscripts.

## Front Matter Kinds

| Kind | Description |
|------|-------------|
| `title_page` | Title and author |
| `subtitle` | Subtitle |
| `copyright` | Copyright notice |
| `dedication` | Dedication |
| `epigraph` | Epigraph |
| `preface` | Preface |
| `introduction` | Introduction |
| `foreword` | Foreword |
| `disclaimer` | Disclaimer |
| `custom` | Custom block |

## Back Matter Kinds

| Kind | Description |
|------|-------------|
| `acknowledgements` | Acknowledgements |
| `about_author` | About the Author |
| `author_note` | Author note |
| `resources` | Resources |
| `next_book` | Next book / series page |
| `call_to_action` | Call to action |
| `workbook_appendix` | Workbook appendix |
| `references` | References / bibliography |
| `glossary` | Glossary |
| `bonus_material` | Bonus material note |
| `custom` | Custom block |

## Block Structure

```json
{
  "kind": "dedication",
  "title": "Dedication",
  "content": "For my family.",
  "sort_order": 0
}
```

- `kind` – Block type
- `title` – Optional display title
- `content` – Body text
- `sort_order` – Order within front/back matter

## Optional Inclusion

- Per export profile
- Per export request
- Front/back matter blocks are stored in profiles and can be overridden at export time

## ExportParams

Legacy flat fields in `ExportParams`:

- `copyright_notice`
- `dedication`
- `epigraph`
- `front_matter` (raw text)
- `acknowledgements`
- `author_bio`
- `back_matter` (raw text)

These map to structured blocks for backward compatibility. New profiles should use `front_matter_blocks` and `back_matter_blocks`.
