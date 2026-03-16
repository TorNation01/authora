"""Configurable export filename generation."""

from datetime import date
from typing import Any


def get_export_filename(
    book_title: str,
    fmt: str,
    *,
    backup_style: bool = False,
    suffix: str | None = None,
    profile_name: str | None = None,
    version: str | None = None,
    author_name: str | None = None,
    pattern: str | None = None,
) -> str:
    """
    Generate export filename from pattern or defaults.

    Pattern placeholders:
        {project_title} - book/project title
        {profile} - export profile name
        {date} - YYYY-MM-DD
        {version} - draft version
        {author} - author name

    Default when no pattern: ProjectName.ext or ProjectName_suffix.ext
    """
    safe_title = "".join(
        c if c.isalnum() or c in " -_" else "_" for c in (book_title or "manuscript")
    ).strip()[:50]
    if not safe_title:
        safe_title = "manuscript"

    ext = fmt.lower()
    today = date.today().isoformat()

    if suffix:
        return f"{safe_title}{suffix}.{ext}"
    if backup_style:
        return f"{safe_title}-backup-{today}.{ext}"

    if pattern:
        name = pattern.format(
            project_title=safe_title,
            profile=profile_name or "Export",
            date=today,
            version=version or "1",
            author=(author_name or "Author").replace(" ", "_")[:30],
        )
        # Sanitize
        name = "".join(c if c.isalnum() or c in " -_." else "_" for c in name).strip()
        if not name:
            name = safe_title
        return f"{name}.{ext}"

    return f"{safe_title}.{ext}"
