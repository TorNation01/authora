# CSL Style Support

AUTHORA uses Citation Style Language (CSL) for formatting citations and bibliographies.

## Format

CSL is an XML-based format. Styles define:

- In-text citation format (e.g. (Author, 2024) or [1])
- Bibliography entry format
- Punctuation, abbreviations, order of elements

## Style Sources

1. **citeproc-py-styles** — Python package with common styles (APA, MLA, Chicago, etc.)
2. **Database** — `citation_styles` table for custom styles
3. **Custom XML** — Pass `style_xml` when style not in built-in set

## Style Resolution

```
1. If style_xml provided → use temp file
2. If citeproc-py-styles installed → get_style_filepath(slug)
3. Fallback: authora/data/csl/{slug}.csl or ./csl/{slug}.csl
4. Else: pass slug to CitationStylesStyle (may use package default)
```

## Adding Custom Styles

1. Download CSL from [style repository](https://github.com/citation-style-language/styles)
2. Insert into `citation_styles` table with `csl_xml` and `slug`
3. Or place `.csl` file in `authora/data/csl/`

## Footnote/Endnote

CSL styles can include footnote and endnote variants. The style file defines the citation format. AUTHORA can support footnote-capable styles when the CSL supports it.
