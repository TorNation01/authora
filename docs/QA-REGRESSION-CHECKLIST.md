# AUTHORA Regression Checklist

Use before each release to verify core flows remain functional.

---

## Auth & Onboarding

- [ ] Register with valid email/password
- [ ] Login with valid credentials
- [ ] Login with invalid credentials shows error
- [ ] Logout clears session
- [ ] Post-register redirect to onboarding or dashboard
- [ ] Onboarding steps complete (book type, mode, goals, etc.)
- [ ] Skip onboarding when available

## Book Creation & Projects

- [ ] Create project
- [ ] Create fiction book
- [ ] Create nonfiction book
- [ ] List projects
- [ ] List books in project
- [ ] Update/delete project
- [ ] Update/delete book

## Fiction Flow

- [ ] Fiction workspace loads
- [ ] Create character
- [ ] Create plot arc
- [ ] Create scene
- [ ] Chapter plans

## Nonfiction Flow

- [ ] Nonfiction workspace loads
- [ ] Create audience
- [ ] Create chapter plan
- [ ] Create transformation framework

## Ghostwriter Flow

- [ ] Ghostwriter workspace loads
- [ ] Submit intake
- [ ] Generate outline (if AI configured)
- [ ] Apply draft to chapter

## Editor & Chapters

- [ ] Create chapter
- [ ] Edit chapter content
- [ ] Autosave triggers
- [ ] Version history loads
- [ ] Delete chapter

## Notes & Highlights

- [ ] Create project note
- [ ] Create book note
- [ ] Search notes
- [ ] Attach file to note (if supported)

## AI Assist

- [ ] AI actions list loads
- [ ] Run AI action (expand, improve, etc.) when AI configured
- [ ] Safety filter blocks inappropriate prompts

## Dictionary/Thesaurus

- [ ] Lookup word
- [ ] Thesaurus synonyms

## Accountability

- [ ] Accountability settings load
- [ ] Update daily/weekly goals
- [ ] Reminder settings

## Reminders

- [ ] Reminders list (admin)
- [ ] Create reminder
- [ ] Cron runs (if CRON_SECRET set)

## Gamification

- [ ] Stats load
- [ ] Achievements display
- [ ] XP/streak updates

## Finish Mode & Export

- [ ] Export preview
- [ ] Export TXT
- [ ] Export DOCX
- [ ] Export EPUB
- [ ] Publishing prep tools

## Setup Wizard

- [ ] Setup status (standalone)
- [ ] Apply setup steps
- [ ] Admin creation

## Admin

- [ ] Admin overview loads
- [ ] User list
- [ ] Feature flags
- [ ] Export jobs
- [ ] Health/readiness
- [ ] Audit logs
- [ ] Support notes

## API Health

- [ ] GET /health returns 200
- [ ] GET /health/ready returns 200 or 503
