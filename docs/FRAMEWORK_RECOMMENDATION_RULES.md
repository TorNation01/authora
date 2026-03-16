# Framework Recommendation Rules

The recommendation engine scores frameworks based on:

1. **Book type** – fiction vs nonfiction (filter)
2. **Genre** – match against `ideal_genres` or `recommendation_rules.genres` / `ideal_genres`
3. **Template** – template slug hints (e.g. romance → romance_beats, thriller → mystery_thriller)
4. **Series intent** – `is_series=true` boosts `series_arc`
5. **Featured** – featured frameworks get a small boost

## Scoring Logic

- Base score: 0.5
- Genre match: +weight (0.5–1.0 from recommendation_rules)
- High weight (>0.8): +0.2
- Featured: +0.15
- Series + series_arc: +0.5
- Template-specific boosts (see below)

## Template → Framework Mapping

| Template slug contains | Framework | Boost |
|------------------------|-----------|-------|
| romance | romance_beats | +0.5 |
| thriller, mystery | mystery_thriller | +0.5 |
| fantasy, scifi | hero_journey | +0.3 |
| memoir | memoir_lesson | +0.5 |
| workbook | workbook | +0.5 |
| selfhelp | step_by_step | +0.3 |
| business | authority | +0.5 |

## Framework → Genre Mapping

| Framework | Ideal genres |
|-----------|-------------|
| three_act | General Fiction, Thriller, Mystery, Science Fiction, Fantasy, Contemporary |
| hero_journey | Fantasy, Science Fiction, Young Adult, Adventure |
| save_the_cat | Thriller, Romance, Mystery, Contemporary, Young Adult |
| romance_beats | Romance |
| mystery_thriller | Thriller, Mystery, Crime, Suspense |
| series_arc | Fantasy, Science Fiction, Romance, Series |
| character_driven | Literary Fiction, Contemporary, Women's Fiction |
| problem_solution_result | Self-Help, Business, How-To |
| step_by_step | Self-Help, Health, Finance, Personal Development |
| authority | Business, Professional, Thought Leadership |
| instructional | Educational, How-To, Professional |
| workbook | Workbook, Self-Help, Educational |
| memoir_lesson | Memoir |
| modular | General Non-fiction, Reference, Essay |

## Examples

- **Romance fiction** → romance_beats or three_act
- **Thriller** → mystery_thriller or three_act
- **Fantasy epic** → hero_journey or series_arc
- **Self-help** → step_by_step
- **Business authority book** → authority
- **Workbook** → workbook
- **Memoir** → memoir_lesson
