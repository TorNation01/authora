"""CSL citation and bibliography generation using citeproc-py."""

import logging
from pathlib import Path
from typing import Any

from citeproc import CitationStylesBibliography, CitationStylesStyle, formatter
from citeproc import Citation as ProcCitation, CitationItem
from citeproc.source.json import CiteProcJSON

logger = logging.getLogger(__name__)

# Built-in style slugs supported via citeproc-py-styles
BUILTIN_STYLE_SLUGS = ("apa", "mla", "chicago-author-date", "harvard1", "ieee", "mhra")


def _get_style_path(slug: str) -> str | None:
    """Resolve CSL style file path. Uses citeproc-py-styles if available."""
    try:
        from citeproc_styles import get_style_filepath
        return get_style_filepath(slug)
    except ImportError:
        pass
    # Fallback: check common locations
    for base in [Path(__file__).parent.parent / "data" / "csl", Path.cwd() / "csl"]:
        p = base / f"{slug}.csl"
        if p.exists():
            return str(p)
    return None


def _ensure_csl_id(ref: dict) -> dict:
    """Ensure CSL ref has 'id' (citeproc expects lowercase)."""
    ref = dict(ref)
    if "id" not in ref and "key" in ref:
        ref["id"] = str(ref["key"]).lower()
    elif "id" in ref:
        ref["id"] = str(ref["id"]).lower()
    return ref


def render_citation(
    refs: list[dict[str, Any]],
    citation_keys: list[str],
    style_slug: str = "apa",
    style_xml: str | None = None,
    format_type: str = "plain",
) -> str:
    """
    Render a single in-text citation for the given keys.
    refs: list of CSL JSON objects
    citation_keys: list of ref ids to cite (e.g. ["abc123", "def456"])
    style_slug: style identifier (apa, mla, etc.)
    style_xml: optional raw CSL XML if style_slug not built-in
    format_type: plain | html
    Returns formatted citation string.
    """
    if not refs or not citation_keys:
        return ""
    refs = [_ensure_csl_id(r) for r in refs]
    try:
        source = CiteProcJSON(refs)
        formatter_cls = formatter.plain if format_type == "plain" else formatter.html
        if style_xml:
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csl", delete=False) as f:
                f.write(style_xml)
                f.flush()
            bib_style = CitationStylesStyle(f.name, validate=False)
        else:
            path = _get_style_path(style_slug)
            bib_style = CitationStylesStyle(path or style_slug, validate=False)
        bib = CitationStylesBibliography(bib_style, source, formatter_cls)
        items = [CitationItem(k.lower()) for k in citation_keys]
        citation = ProcCitation(items)
        bib.register(citation)

        def warn(ci):
            logger.warning("Citation key not found: %s", ci.key)

        return bib.cite(citation, warn) or ""
    except Exception as e:
        logger.exception("CSL citation render failed: %s", e)
        return ""


def render_bibliography(
    refs: list[dict[str, Any]],
    citation_keys: list[str] | None = None,
    style_slug: str = "apa",
    style_xml: str | None = None,
    format_type: str = "plain",
) -> list[str]:
    """
    Render bibliography entries for refs.
    If citation_keys provided, only include those refs; otherwise all.
    Returns list of formatted bibliography entry strings.
    """
    if not refs:
        return []
    refs = [_ensure_csl_id(r) for r in refs]
    keys_to_include = {r.get("id", "").lower() for r in refs}
    if citation_keys:
        keys_to_include = {k.lower() for k in citation_keys}
    filtered = [r for r in refs if r.get("id", "").lower() in keys_to_include]
    if not filtered:
        return []
    try:
        source = CiteProcJSON(filtered)
        formatter_cls = formatter.plain if format_type == "plain" else formatter.html
        if style_xml:
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csl", delete=False) as f:
                f.write(style_xml)
                f.flush()
            bib_style = CitationStylesStyle(f.name, validate=False)
        else:
            path = _get_style_path(style_slug)
            bib_style = CitationStylesStyle(path or style_slug, validate=False)
        bib = CitationStylesBibliography(bib_style, source, formatter_cls)
        items = [CitationItem(r["id"]) for r in filtered]
        citation = ProcCitation(items)
        bib.register(citation)

        def warn(ci):
            logger.warning("Citation key not found: %s", ci.key)

        bib.cite(citation, warn)
        return [str(entry) for entry in bib.bibliography()]
    except Exception as e:
        logger.exception("CSL bibliography render failed: %s", e)
        return []
