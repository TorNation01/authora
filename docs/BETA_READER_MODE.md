# Beta Reader Mode

Beta Reader Mode provides a clean, reading-oriented interface for early readers to give feedback without exposing internal author clutter.

## Goals

- **Clean reading** – Reduced editing controls; focus on reading
- **Easy feedback** – Simple comment and reaction tools
- **Chapter-by-chapter** – Optional chapter-level reactions
- **Broad impressions** – End-of-book feedback prompts
- **Spoiler-sensitive** – Optional prompts that avoid spoilers

## Implementation Status

- **Roles** – `beta_reader` role grants view_manuscript, comment, view_notes, view_activity
- **Permissions** – No edit_manuscript; no approve_chapters; no manage_*
- **Content access** – Via `get_project_with_access_or_404` and `get_book_with_access_or_404`

## Future Enhancements

- **Reader UI** – Dedicated reading view with minimal chrome
- **Chapter reactions** – Optional rating/reaction per chapter
- **End-of-book form** – Feedback prompts (pacing, clarity, character connection)
- **Anonymous feedback** – Optional anonymous mode for sensitive feedback

## Architecture Notes

- Beta readers are project members with role `beta_reader`
- Share scope can restrict to `review_copy` or `chapters` for partial sharing
- Comments use `ContentComment` with optional `comment_type` and `collaboration_role`
