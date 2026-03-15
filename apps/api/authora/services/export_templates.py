"""Professional manuscript templates for export.

Supports: self-editing, editor handoff, beta readers, ebook, print, client delivery.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ManuscriptTemplate:
    """Manuscript formatting template."""

    name: str
    font_name: str
    font_size: int
    line_spacing: float
    top_margin_in: float
    bottom_margin_in: float
    left_margin_in: float
    right_margin_in: float
    first_line_indent: float
    header_footer: bool
    scene_break: str


MANUSCRIPT = ManuscriptTemplate(
    name="manuscript",
    font_name="Times New Roman",
    font_size=12,
    line_spacing=2.0,
    top_margin_in=1.0,
    bottom_margin_in=1.0,
    left_margin_in=1.0,
    right_margin_in=1.0,
    first_line_indent=0.5,
    header_footer=True,
    scene_break="***",
)

PRINT = ManuscriptTemplate(
    name="print",
    font_name="Times New Roman",
    font_size=11,
    line_spacing=1.15,
    top_margin_in=0.75,
    bottom_margin_in=0.75,
    left_margin_in=0.75,
    right_margin_in=0.75,
    first_line_indent=0.5,
    header_footer=True,
    scene_break="* * *",
)

EBOOK = ManuscriptTemplate(
    name="ebook",
    font_name="Georgia",
    font_size=12,
    line_spacing=1.5,
    top_margin_in=0.5,
    bottom_margin_in=0.5,
    left_margin_in=0.75,
    right_margin_in=0.75,
    first_line_indent=0.25,
    header_footer=False,
    scene_break="* * *",
)


def get_template(style: str) -> ManuscriptTemplate:
    """Get template by style name."""
    if style == "print":
        return PRINT
    if style == "ebook":
        return EBOOK
    return MANUSCRIPT


def front_matter_sections() -> list[dict[str, str]]:
    """Standard front matter section order."""
    return [
        {"key": "copyright", "label": "Copyright Notice", "placeholder": "Copyright © [YEAR] [AUTHOR]. All rights reserved."},
        {"key": "dedication", "label": "Dedication", "placeholder": ""},
        {"key": "epigraph", "label": "Epigraph", "placeholder": ""},
        {"key": "other", "label": "Other", "placeholder": ""},
    ]


def back_matter_sections() -> list[dict[str, str]]:
    """Standard back matter section order."""
    return [
        {"key": "acknowledgements", "label": "Acknowledgements", "placeholder": ""},
        {"key": "about_author", "label": "About the Author", "placeholder": ""},
        {"key": "other", "label": "Other", "placeholder": ""},
    ]
