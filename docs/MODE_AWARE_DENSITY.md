# Mode-Aware Density Behaviour

The Story Density Engine adapts to project guidance mode.

## Guided Mode

- Stronger checks
- Framework-aware density analysis
- Stronger detection of missing support around key beats/stages
- More active trim/strengthen suggestions

## Flexible Mode

- Softer assumptions
- Less structural bias
- Stronger tolerance for cross-genre pacing
- Focus on repeated beats, drag, and support quality

## Freeform Mode

- No formula enforcement
- No rigid pacing assumptions
- GeneralDensityDetector only (no fiction/nonfiction/memoir/workbook-specific detectors)
- Detect repetition, clutter, thinness, chapter-purpose weakness
- Preserve artistic and experimental space

## Detector Selection

```python
def get_density_detectors_for_project(project_type, guidance_mode):
    if guidance_mode == "freeform":
        return [GeneralDensityDetector]
    always = [GeneralDensityDetector]
    if project_type == "fiction":
        always.append(FictionDensityDetector)
    elif project_type == "nonfiction":
        always.append(NonfictionDensityDetector)
    # ... memoir, workbook, hybrid
    return always
```

## User Controls (Future)

- Reduce density strictness
- Disable certain issue classes
- Suppress framework assumptions
- Mark density choices as intentional
- Disable continuous density scanning
