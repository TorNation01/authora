"""Academic, course, lecture, essay, and study-writing template definitions for AUTHORA.

Expands AUTHORA beyond books into academic and educational writing workflows.
Each template includes structure, section scaffolds, guidance text, AI prompt hooks,
citation/reference integration points, export recommendations, and academic tone guidance.
"""

from typing import Any

# Shared academic planning sections
ACADEMIC_CITATION_SECTIONS = [
    {"id": "sources", "title": "Sources & References", "type": "section", "guidance": "List all sources. Use AUTHORA Vault or reference manager. Note citation style (APA, MLA, Chicago)."},
    {"id": "references", "title": "Reference List / Bibliography", "type": "section", "guidance": "Full citations. Export-ready format. Verify against style guide."},
]

ACADEMIC_REVISION_SECTION = {"id": "revision", "title": "Revision Notes", "type": "section", "guidance": "Clarity, coherence, argument strength, citation accuracy."}

# Academic tone guidance (stored in default_structure for UI)
ACADEMIC_TONE_GUIDANCE = {
    "formal": "Use formal third person unless instructed otherwise. Avoid contractions, colloquialisms, and personal anecdotes unless relevant.",
    "objective": "Present evidence and analysis objectively. Acknowledge counterarguments. Distinguish fact from interpretation.",
    "precise": "Choose precise vocabulary. Define technical terms on first use. Avoid vague qualifiers (very, really, quite).",
}

# Default accountability for academic work
ACADEMIC_ACCOUNTABILITY = {
    "reminder_frequency": "weekly",
    "goal_type": "words",
    "default_target_words": 500,
    "check_in_prompts": ["What sources did you add this week?", "What section will you draft next?"],
}

# Citation integration note for templates
CITATION_INTEGRATION = {
    "vault_sources": True,
    "reference_manager": "Zotero/Mendeley compatible",
    "style_options": ["APA", "MLA", "Chicago", "Harvard"],
}


def _academic_base(
    slug: str,
    name: str,
    description: str,
    category: str,
    parent_slug: str | None,
    planning_sections: list[dict],
    chapter_skeletons: list[dict],
    milestones: list[dict],
    ai_prompts: dict[str, str],
    sort_order: int,
    **overrides: Any,
) -> dict[str, Any]:
    """Base academic template."""
    return {
        "slug": slug,
        "category": category,
        "parent_slug": parent_slug,
        "name": name,
        "description": description,
        "who_it_is_for": "Students, educators, and academic writers.",
        "expected_outcome": "A well-structured, citation-ready academic document.",
        "suggested_workflow": "Plan → Draft → Cite → Revise → Export.",
        "book_type": "nonfiction",
        "genre": "Academic",
        "structure_framework": "academic",
        "default_structure": {
            "planning_sections": planning_sections,
            "tone_guidance": ACADEMIC_TONE_GUIDANCE,
            "citation_integration": CITATION_INTEGRATION,
        },
        "default_milestones": milestones,
        "default_planning_prompts": {
            "topic": "What is your topic or research question?",
            "thesis": "What is your main argument or claim?",
            "sources": "What key sources will you use?",
        },
        "default_accountability": ACADEMIC_ACCOUNTABILITY,
        "ai_prompts": ai_prompts,
        "export_recommendations": ["docx", "pdf"],
        "setup_questions": [
            {"id": "topic", "prompt": "What is your topic or research question?", "type": "text"},
            {"id": "citation_style", "prompt": "Which citation style?", "type": "select", "options": ["APA", "MLA", "Chicago", "Harvard"]},
            {"id": "word_target", "prompt": "Target word count (if applicable)?", "type": "number"},
        ],
        "chapter_skeletons": chapter_skeletons,
        "sort_order": sort_order,
        "is_featured": False,
        "is_disabled": False,
        "access_level": "free",
        "premium_pack_slug": None,
        **overrides,
    }


# ---------------------------------------------------------------------------
# ESSAY TEMPLATES
# ---------------------------------------------------------------------------

ESSAY_PLANNING = [
    {"id": "topic", "title": "Topic & Research Question", "type": "text", "guidance": "Narrow your focus. One clear question or claim."},
    {"id": "thesis", "title": "Thesis Statement", "type": "text", "guidance": "One sentence that states your main argument. Debatable, specific, supportable."},
    {"id": "main_points", "title": "Main Points / Outline", "type": "section", "guidance": "2–5 main points that support your thesis. One paragraph per point."},
    {"id": "counterarguments", "title": "Counterarguments (if applicable)", "type": "section", "guidance": "Anticipate objections. How will you address them?"},
    {"id": "sources", "title": "Sources & References", "type": "section", "guidance": "Key sources. Note citation style."},
    ACADEMIC_REVISION_SECTION,
]

ESSAY_AI_PROMPTS = {
    "thesis": "Help me refine this thesis statement to be more specific and arguable.",
    "outline": "Help me develop main points that support my thesis.",
    "transition": "Help me write a transition between these two paragraphs.",
    "conclusion": "Help me strengthen my conclusion without introducing new ideas.",
}

ESSAY_MILESTONES = [
    {"id": "thesis", "label": "Thesis and outline complete", "type": "planning"},
    {"id": "draft", "label": "First draft complete", "type": "draft"},
    {"id": "citations", "label": "Citations added", "type": "draft"},
    {"id": "revision", "label": "Revision complete", "type": "revision"},
    {"id": "final", "label": "Final polish", "type": "revision"},
]

# Standard essay
STANDARD_ESSAY_SKELETON = [
    {"title": "Introduction", "summary": "Hook, context, thesis statement. 10–15% of length."},
    {"title": "Body Paragraph 1", "summary": "First main point with evidence and analysis."},
    {"title": "Body Paragraph 2", "summary": "Second main point with evidence and analysis."},
    {"title": "Body Paragraph 3", "summary": "Third main point (add more as needed)."},
    {"title": "Conclusion", "summary": "Restate thesis, summarize key points, closing thought. No new evidence."},
    {"title": "References", "summary": "Full reference list in chosen citation style."},
]

# Argumentative essay (add counterargument section)
ARGUMENTATIVE_ESSAY_SKELETON = [
    {"title": "Introduction", "summary": "Hook, context, thesis (clear position on debatable issue)."},
    {"title": "Body 1 – Claim 1", "summary": "First supporting claim with evidence."},
    {"title": "Body 2 – Claim 2", "summary": "Second supporting claim with evidence."},
    {"title": "Body 3 – Claim 3", "summary": "Third supporting claim with evidence."},
    {"title": "Counterargument & Rebuttal", "summary": "Acknowledge opposing view. Rebut with evidence."},
    {"title": "Conclusion", "summary": "Restate thesis, reinforce argument, call to action or implication."},
    {"title": "References", "summary": "Full reference list."},
]

# Persuasive essay
PERSUASIVE_ESSAY_SKELETON = [
    {"title": "Introduction", "summary": "Hook, establish credibility, state position."},
    {"title": "Body 1 – Ethos", "summary": "Appeal to credibility and authority."},
    {"title": "Body 2 – Pathos", "summary": "Appeal to emotion (appropriately)."},
    {"title": "Body 3 – Logos", "summary": "Appeal to logic and evidence."},
    {"title": "Conclusion", "summary": "Call to action. Leave reader motivated."},
    {"title": "References", "summary": "Full reference list."},
]

# Analytical essay
ANALYTICAL_ESSAY_SKELETON = [
    {"title": "Introduction", "summary": "Introduce subject, state analytical focus, preview findings."},
    {"title": "Analysis Section 1", "summary": "First element or dimension of analysis."},
    {"title": "Analysis Section 2", "summary": "Second element or dimension."},
    {"title": "Analysis Section 3", "summary": "Third element or dimension."},
    {"title": "Conclusion", "summary": "Synthesize analysis. What does it reveal? So what?"},
    {"title": "References", "summary": "Full reference list."},
]

# Compare and contrast
COMPARE_CONTRAST_SKELETON = [
    {"title": "Introduction", "summary": "Introduce both subjects, state basis for comparison, thesis."},
    {"title": "Subject A – Key Points", "summary": "Overview of first subject."},
    {"title": "Subject B – Key Points", "summary": "Overview of second subject."},
    {"title": "Comparison – Similarities", "summary": "Where do they align?"},
    {"title": "Contrast – Differences", "summary": "Where do they differ? Significance?"},
    {"title": "Conclusion", "summary": "Synthesis. Which is preferable or more effective? Why?"},
    {"title": "References", "summary": "Full reference list."},
]

# Reflective essay
REFLECTIVE_ESSAY_SKELETON = [
    {"title": "Introduction", "summary": "Context. What experience or material are you reflecting on?"},
    {"title": "Description", "summary": "What happened? Key events or content. Objective summary."},
    {"title": "Analysis", "summary": "What did you learn? How did it change your thinking?"},
    {"title": "Evaluation", "summary": "What worked? What would you do differently?"},
    {"title": "Conclusion", "summary": "Future application. What will you take forward?"},
    {"title": "References", "summary": "If applicable."},
]

# Expository essay
EXPOSITORY_ESSAY_SKELETON = [
    {"title": "Introduction", "summary": "Introduce topic. Preview what you will explain."},
    {"title": "Explanation 1", "summary": "First aspect or step. Clear, logical."},
    {"title": "Explanation 2", "summary": "Second aspect or step."},
    {"title": "Explanation 3", "summary": "Third aspect or step."},
    {"title": "Conclusion", "summary": "Summarize. Reinforce understanding."},
    {"title": "References", "summary": "Full reference list."},
]

# Descriptive essay
DESCRIPTIVE_ESSAY_SKELETON = [
    {"title": "Introduction", "summary": "Introduce subject. Set the scene."},
    {"title": "Description – Sensory Detail", "summary": "Sight, sound, touch, smell. Show, don't tell."},
    {"title": "Description – Structure/Organization", "summary": "Spatial or logical order. Guide the reader."},
    {"title": "Description – Significance", "summary": "Why does this matter? Emotional or thematic resonance."},
    {"title": "Conclusion", "summary": "Leave reader with lasting impression."},
    {"title": "References", "summary": "If applicable."},
]

# Critical response essay
CRITICAL_RESPONSE_SKELETON = [
    {"title": "Introduction", "summary": "Introduce text/work. State your critical focus."},
    {"title": "Summary", "summary": "Brief, objective summary of the work. No evaluation yet."},
    {"title": "Analysis", "summary": "Strengths and weaknesses. Evidence from the work."},
    {"title": "Evaluation", "summary": "Your judgment. Criteria for evaluation."},
    {"title": "Conclusion", "summary": "Overall assessment. Significance of the work."},
    {"title": "References", "summary": "Primary text + any secondary sources."},
]

# Case study essay
CASE_STUDY_ESSAY_SKELETON = [
    {"title": "Introduction", "summary": "Introduce case. State analytical framework."},
    {"title": "Case Background", "summary": "Context, key facts, relevant history."},
    {"title": "Analysis", "summary": "Apply theory/framework. What does the case illustrate?"},
    {"title": "Discussion", "summary": "Implications. Limitations. Comparison to similar cases."},
    {"title": "Conclusion", "summary": "Key takeaways. Recommendations if applicable."},
    {"title": "References", "summary": "Case sources + theoretical framework."},
]

# Timed essay outline
TIMED_ESSAY_SKELETON = [
    {"title": "Quick Outline (2–3 min)", "summary": "Thesis + 3 main points. One line each."},
    {"title": "Introduction (5 min)", "summary": "Hook + thesis. Keep it tight."},
    {"title": "Body 1", "summary": "Point 1 + evidence + analysis."},
    {"title": "Body 2", "summary": "Point 2 + evidence + analysis."},
    {"title": "Body 3", "summary": "Point 3 + evidence + analysis."},
    {"title": "Conclusion (2 min)", "summary": "Restate thesis. One-sentence close."},
]


# ---------------------------------------------------------------------------
# RESEARCH / ACADEMIC TEMPLATES
# ---------------------------------------------------------------------------

RESEARCH_PLANNING = [
    {"id": "research_question", "title": "Research Question", "type": "text", "guidance": "Clear, focused, answerable question."},
    {"id": "thesis", "title": "Thesis / Hypothesis", "type": "text", "guidance": "Your proposed answer or claim."},
    {"id": "literature", "title": "Literature Notes", "type": "section", "guidance": "Key sources. Gaps in existing research."},
    {"id": "methodology", "title": "Methodology Notes", "type": "section", "guidance": "Approach, design, data sources."},
    {"id": "outline", "title": "Full Outline", "type": "section", "guidance": "Section-by-section plan."},
    *ACADEMIC_CITATION_SECTIONS,
    ACADEMIC_REVISION_SECTION,
]

RESEARCH_AI_PROMPTS = {
    "lit_review": "Help me synthesize these sources into a coherent literature review paragraph.",
    "methodology": "Help me describe my methodology clearly and concisely.",
    "results": "Help me present these findings objectively.",
    "discussion": "Help me interpret these results and connect to the literature.",
}

RESEARCH_MILESTONES = [
    {"id": "proposal", "label": "Proposal / outline approved", "type": "planning"},
    {"id": "lit_review", "label": "Literature review draft", "type": "draft"},
    {"id": "methods", "label": "Methods section draft", "type": "draft"},
    {"id": "results", "label": "Results / findings draft", "type": "draft"},
    {"id": "discussion", "label": "Discussion draft", "type": "draft"},
    {"id": "citations", "label": "Citations complete", "type": "draft"},
    {"id": "revision", "label": "Revision complete", "type": "revision"},
    {"id": "final", "label": "Final submission", "type": "revision"},
]

# Research paper (IMRaD)
RESEARCH_PAPER_SKELETON = [
    {"title": "Abstract", "summary": "150–250 words. Purpose, methods, key findings, implications."},
    {"title": "Introduction", "summary": "Context, gap, research question, thesis, roadmap."},
    {"title": "Literature Review", "summary": "Synthesize relevant research. Establish gap."},
    {"title": "Methodology", "summary": "Design, participants, materials, procedure, analysis."},
    {"title": "Results", "summary": "Present findings. No interpretation yet."},
    {"title": "Discussion", "summary": "Interpret results. Limitations. Implications. Future research."},
    {"title": "Conclusion", "summary": "Restate contribution. Closing thought."},
    {"title": "References", "summary": "Full reference list."},
]

# Literature review
LIT_REVIEW_SKELETON = [
    {"title": "Introduction", "summary": "Scope, purpose, organization of the review."},
    {"title": "Theme 1", "summary": "First thematic cluster of sources."},
    {"title": "Theme 2", "summary": "Second thematic cluster."},
    {"title": "Theme 3", "summary": "Third thematic cluster."},
    {"title": "Synthesis & Gap", "summary": "What is known? What is missing?"},
    {"title": "Conclusion", "summary": "Implications for your research."},
    {"title": "References", "summary": "Annotated or full list."},
]

# Annotated bibliography
ANNOTATED_BIB_SKELETON = [
    {"title": "Source 1", "summary": "Citation + annotation (summary, relevance, evaluation)."},
    {"title": "Source 2", "summary": "Citation + annotation."},
    {"title": "Source 3", "summary": "Citation + annotation."},
    {"title": "Source 4", "summary": "Citation + annotation."},
    {"title": "Source 5", "summary": "Citation + annotation. Add more as needed."},
]

# Thesis/dissertation planning
THESIS_PLANNING_SKELETON = [
    {"title": "Abstract", "summary": "250–350 words. Full thesis summary."},
    {"title": "Chapter 1 – Introduction", "summary": "Background, problem, research questions, significance."},
    {"title": "Chapter 2 – Literature Review", "summary": "Comprehensive review. Theoretical framework."},
    {"title": "Chapter 3 – Methodology", "summary": "Design, participants, instruments, procedure, analysis."},
    {"title": "Chapter 4 – Results", "summary": "Findings. Tables and figures."},
    {"title": "Chapter 5 – Discussion", "summary": "Interpretation, limitations, implications."},
    {"title": "Chapter 6 – Conclusion", "summary": "Summary, contributions, future research."},
    {"title": "References", "summary": "Full bibliography."},
    {"title": "Appendices", "summary": "Instruments, consent forms, supplementary data."},
]

# Capstone project report
CAPSTONE_SKELETON = [
    {"title": "Executive Summary", "summary": "1-page overview of project and outcomes."},
    {"title": "Introduction", "summary": "Problem, objectives, scope."},
    {"title": "Background / Literature", "summary": "Context and prior work."},
    {"title": "Methodology", "summary": "Approach, tools, process."},
    {"title": "Implementation / Results", "summary": "What was built or achieved."},
    {"title": "Evaluation", "summary": "Assessment against objectives."},
    {"title": "Conclusion", "summary": "Reflection, lessons learned."},
    {"title": "References", "summary": "Full reference list."},
]

# Journal article
JOURNAL_ARTICLE_SKELETON = [
    {"title": "Abstract", "summary": "Structured or unstructured. 150–250 words."},
    {"title": "Introduction", "summary": "Brief. Gap, aim, contribution."},
    {"title": "Literature / Theory", "summary": "Focused. Establish position."},
    {"title": "Methods", "summary": "Concise. Reproducible."},
    {"title": "Results", "summary": "Findings. Figures/tables."},
    {"title": "Discussion", "summary": "Interpretation. Limitations."},
    {"title": "Conclusion", "summary": "Short. Implications."},
    {"title": "References", "summary": "Journal style."},
]

# Conference paper
CONFERENCE_PAPER_SKELETON = [
    {"title": "Abstract", "summary": "150–200 words. Often required separately."},
    {"title": "Introduction", "summary": "Problem, contribution. Hook quickly."},
    {"title": "Background", "summary": "Brief. Enough for conference audience."},
    {"title": "Approach / Method", "summary": "What you did."},
    {"title": "Results", "summary": "Key findings."},
    {"title": "Discussion", "summary": "Implications. Future work."},
    {"title": "Conclusion", "summary": "Takeaway message."},
    {"title": "References", "summary": "Conference limit often applies."},
]

# Discussion paper
DISCUSSION_PAPER_SKELETON = [
    {"title": "Introduction", "summary": "Issue, stakes, your position."},
    {"title": "Context", "summary": "Background. Why this matters now."},
    {"title": "Argument 1", "summary": "First main argument."},
    {"title": "Argument 2", "summary": "Second main argument."},
    {"title": "Counterarguments", "summary": "Address objections."},
    {"title": "Conclusion", "summary": "Recommendations or implications."},
    {"title": "References", "summary": "Full list."},
]

# Methodology section builder
METHODOLOGY_BUILDER_SKELETON = [
    {"title": "Research Design", "summary": "Qualitative, quantitative, mixed. Justify."},
    {"title": "Participants / Sample", "summary": "Who, how many, how selected."},
    {"title": "Materials / Instruments", "summary": "Surveys, protocols, tools."},
    {"title": "Procedure", "summary": "Step-by-step. Reproducible."},
    {"title": "Data Analysis", "summary": "How you analyzed the data."},
    {"title": "Ethics", "summary": "Consent, approval, confidentiality."},
]

# Results/discussion structure
RESULTS_DISCUSSION_SKELETON = [
    {"title": "Results – Finding 1", "summary": "Present objectively. Table/figure if applicable."},
    {"title": "Results – Finding 2", "summary": "Present objectively."},
    {"title": "Results – Finding 3", "summary": "Present objectively."},
    {"title": "Discussion – Interpretation", "summary": "What do the results mean?"},
    {"title": "Discussion – Limitations", "summary": "Study limitations."},
    {"title": "Discussion – Implications", "summary": "So what? Future research."},
]

# Reference-heavy paper
REFERENCE_HEAVY_SKELETON = [
    {"title": "Introduction", "summary": "Frame the debate. Your position."},
    {"title": "Section 1", "summary": "Heavy citation. Engage sources directly."},
    {"title": "Section 2", "summary": "Heavy citation. Compare/contrast sources."},
    {"title": "Section 3", "summary": "Heavy citation. Synthesize."},
    {"title": "Conclusion", "summary": "Your contribution to the conversation."},
    {"title": "References", "summary": "Extended bibliography."},
]


# ---------------------------------------------------------------------------
# COURSE / LECTURE TEMPLATES
# ---------------------------------------------------------------------------

COURSE_PLANNING = [
    {"id": "learning_objectives", "title": "Learning Objectives", "type": "section", "guidance": "What should students know or be able to do? Use action verbs (analyze, apply, evaluate)."},
    {"id": "key_concepts", "title": "Key Concepts", "type": "section", "guidance": "Core ideas to cover. Prerequisites."},
    {"id": "activities", "title": "Activities & Engagement", "type": "section", "guidance": "Discussion, exercises, group work."},
    {"id": "materials", "title": "Materials & Resources", "type": "section", "guidance": "Readings, slides, handouts."},
    ACADEMIC_REVISION_SECTION,
]

COURSE_AI_PROMPTS = {
    "objectives": "Help me write clear learning objectives using Bloom's taxonomy verbs.",
    "summary": "Help me summarize this section for students.",
    "discussion": "Help me generate discussion questions for this topic.",
}

COURSE_MILESTONES = [
    {"id": "outline", "label": "Outline complete", "type": "planning"},
    {"id": "draft", "label": "First draft complete", "type": "draft"},
    {"id": "revision", "label": "Revision complete", "type": "revision"},
    {"id": "final", "label": "Ready for delivery", "type": "revision"},
]

# Lecture notes
LECTURE_NOTES_SKELETON = [
    {"title": "Topic & Date", "summary": "Title, course, session date."},
    {"title": "Learning Objectives", "summary": "2–5 objectives. What students will learn."},
    {"title": "Key Concepts", "summary": "Main ideas. Definitions. Frameworks."},
    {"title": "Content Outline", "summary": "Detailed notes. Bullet points, examples."},
    {"title": "Examples & Applications", "summary": "Concrete examples. Case studies."},
    {"title": "Summary & Takeaways", "summary": "Recap. Key points to remember."},
    {"title": "References / Further Reading", "summary": "Sources for students."},
]

# Lecture script
LECTURE_SCRIPT_SKELETON = [
    {"title": "Opening", "summary": "Hook. State objectives. 1–2 min."},
    {"title": "Section 1", "summary": "Full script. Timing noted."},
    {"title": "Section 2", "summary": "Full script. Timing noted."},
    {"title": "Section 3", "summary": "Full script. Timing noted."},
    {"title": "Transitions", "summary": "Between sections. Check understanding."},
    {"title": "Closing", "summary": "Summary. Q&A prompt. Next steps."},
]

# Lesson plan
LESSON_PLAN_SKELETON = [
    {"title": "Lesson Title & Duration", "summary": "Topic, length, grade/course level."},
    {"title": "Learning Objectives", "summary": "Measurable outcomes."},
    {"title": "Materials Needed", "summary": "Handouts, tech, resources."},
    {"title": "Starter / Hook", "summary": "5–10 min. Engage students."},
    {"title": "Main Activity", "summary": "Core content. 20–30 min."},
    {"title": "Practice / Application", "summary": "Students do. 15–20 min."},
    {"title": "Plenary / Wrap-up", "summary": "5 min. Recap. Check understanding."},
    {"title": "Differentiation", "summary": "Support and challenge. Adaptations."},
    {"title": "Homework / Follow-up", "summary": "Assignments. Next lesson link."},
]

# Course module builder
COURSE_MODULE_SKELETON = [
    {"title": "Module Overview", "summary": "Title, duration, objectives."},
    {"title": "Week 1 – Topic", "summary": "Content, activities, readings."},
    {"title": "Week 2 – Topic", "summary": "Content, activities, readings."},
    {"title": "Week 3 – Topic", "summary": "Content, activities, readings."},
    {"title": "Week 4 – Topic", "summary": "Content, activities, readings."},
    {"title": "Assessment", "summary": "Quizzes, assignments, rubric."},
    {"title": "Resources", "summary": "Readings, links, supplementary."},
]

# Seminar handout
SEMINAR_HANDOUT_SKELETON = [
    {"title": "Seminar Title & Date", "summary": "Topic, presenter, session."},
    {"title": "Key Points", "summary": "3–5 main takeaways. Bullet format."},
    {"title": "Discussion Questions", "summary": "Questions for group discussion."},
    {"title": "Readings", "summary": "Required and optional. Page numbers."},
    {"title": "Further Resources", "summary": "Links, references."},
]

# Tutorial guide
TUTORIAL_GUIDE_SKELETON = [
    {"title": "Tutorial Title", "summary": "Topic. Prerequisites."},
    {"title": "Objectives", "summary": "What students will do by the end."},
    {"title": "Step 1", "summary": "First step. Clear instructions."},
    {"title": "Step 2", "summary": "Second step."},
    {"title": "Step 3", "summary": "Third step."},
    {"title": "Troubleshooting", "summary": "Common issues. Solutions."},
    {"title": "Extension", "summary": "Optional. For faster students."},
]

# Workshop outline
WORKSHOP_OUTLINE_SKELETON = [
    {"title": "Workshop Overview", "summary": "Title, duration, audience, goals."},
    {"title": "Icebreaker", "summary": "5–10 min. Get participants engaged."},
    {"title": "Activity 1", "summary": "Main activity. 20–30 min."},
    {"title": "Activity 2", "summary": "Second activity."},
    {"title": "Activity 3", "summary": "Third activity."},
    {"title": "Debrief", "summary": "Reflection. Share outcomes."},
    {"title": "Resources", "summary": "Handouts. Follow-up materials."},
]

# Course workbook
COURSE_WORKBOOK_SKELETON = [
    {"title": "Workbook Introduction", "summary": "How to use. Learning path."},
    {"title": "Unit 1", "summary": "Content + exercises + reflection."},
    {"title": "Unit 2", "summary": "Content + exercises + reflection."},
    {"title": "Unit 3", "summary": "Content + exercises + reflection."},
    {"title": "Self-Assessment", "summary": "Check understanding."},
    {"title": "Answer Key / Notes", "summary": "For facilitators."},
]

# Reading response template
READING_RESPONSE_SKELETON = [
    {"title": "Reading Details", "summary": "Title, author, date. Key citation."},
    {"title": "Summary", "summary": "2–3 sentences. Main argument or content."},
    {"title": "Key Quote", "summary": "One quote that stood out. Page number."},
    {"title": "Response", "summary": "Your reaction. Agree? Disagree? Why?"},
    {"title": "Connection", "summary": "Link to course themes or other readings."},
    {"title": "Question", "summary": "One question for discussion."},
]

# Class discussion guide
CLASS_DISCUSSION_SKELETON = [
    {"title": "Topic", "summary": "What we're discussing. Context."},
    {"title": "Opening Question", "summary": "First question to get discussion started."},
    {"title": "Core Questions", "summary": "2–4 main questions. In logical order."},
    {"title": "Probing Questions", "summary": "Follow-ups to deepen discussion."},
    {"title": "Closing", "summary": "Synthesis. Key takeaways."},
]


# ---------------------------------------------------------------------------
# STUDENT SUPPORT TEMPLATES
# ---------------------------------------------------------------------------

STUDENT_PLANNING = [
    {"id": "goals", "title": "Goals", "type": "section", "guidance": "What do you want to achieve?"},
    {"id": "deadlines", "title": "Deadlines", "type": "section", "guidance": "Key dates. Prioritize."},
    ACADEMIC_REVISION_SECTION,
]

STUDENT_AI_PROMPTS = {
    "summarize": "Help me summarize this passage in my own words.",
    "explain": "Help me explain this concept simply.",
    "quiz": "Help me generate practice questions on this topic.",
}

STUDENT_MILESTONES = [
    {"id": "plan", "label": "Plan complete", "type": "planning"},
    {"id": "draft", "label": "Draft complete", "type": "draft"},
    {"id": "review", "label": "Self-review complete", "type": "revision"},
]

# Study notes
STUDY_NOTES_SKELETON = [
    {"title": "Topic", "summary": "Subject, chapter, date."},
    {"title": "Key Concepts", "summary": "Definitions. Main ideas."},
    {"title": "Examples", "summary": "Worked examples. Applications."},
    {"title": "Connections", "summary": "Link to other topics. Big picture."},
    {"title": "Questions to Review", "summary": "Self-test. Unclear points."},
]

# Assignment planner
ASSIGNMENT_PLANNER_SKELETON = [
    {"title": "Assignment Overview", "summary": "Title, due date, requirements."},
    {"title": "Breakdown", "summary": "Tasks. Estimate time each."},
    {"title": "Schedule", "summary": "When will you do each task?"},
    {"title": "Resources", "summary": "Sources. Help. Office hours."},
    {"title": "Checkpoints", "summary": "Interim deadlines. Draft dates."},
]

# Reading summary
READING_SUMMARY_SKELETON = [
    {"title": "Source", "summary": "Full citation."},
    {"title": "Main Argument", "summary": "1–2 sentences. Thesis."},
    {"title": "Key Points", "summary": "3–5 supporting points."},
    {"title": "Evidence", "summary": "Key evidence or examples."},
    {"title": "Your Notes", "summary": "Relevance. Questions."},
]

# Source analysis
SOURCE_ANALYSIS_SKELETON = [
    {"title": "Source Citation", "summary": "Full reference."},
    {"title": "Authority", "summary": "Author credentials. Publisher. Bias?"},
    {"title": "Purpose", "summary": "Why was this written? Audience?"},
    {"title": "Main Claims", "summary": "What does it argue?"},
    {"title": "Evidence", "summary": "What evidence? Strong or weak?"},
    {"title": "Usefulness", "summary": "How will you use it? Limitations?"},
]

# Revision checklist
REVISION_CHECKLIST_SKELETON = [
    {"title": "Thesis & Argument", "summary": "Clear? Supported? Consistent?"},
    {"title": "Structure", "summary": "Logical flow? Transitions?"},
    {"title": "Evidence", "summary": "Enough? Relevant? Cited?"},
    {"title": "Clarity", "summary": "Precise? Concise? Jargon explained?"},
    {"title": "Citations", "summary": "Style correct? Complete?"},
    {"title": "Mechanics", "summary": "Grammar, spelling, formatting."},
]

# Exam prep outline
EXAM_PREP_SKELETON = [
    {"title": "Exam Details", "summary": "Date, format, topics covered."},
    {"title": "Topic 1 – Summary", "summary": "Key points. Must-know."},
    {"title": "Topic 2 – Summary", "summary": "Key points."},
    {"title": "Topic 3 – Summary", "summary": "Key points."},
    {"title": "Practice Questions", "summary": "Sample Qs. Your answers."},
    {"title": "Weak Spots", "summary": "What to review again."},
]


# ---------------------------------------------------------------------------
# BUILD TEMPLATE LIST
# ---------------------------------------------------------------------------

ACADEMIC_TEMPLATE_DEFINITIONS: list[dict[str, Any]] = [
    # --- ESSAY (parent) ---
    _academic_base(
        "academic-essay",
        "Academic Essay",
        "Structured essays for courses and assessments. Multiple essay types available.",
        "academic",
        None,
        ESSAY_PLANNING,
        STANDARD_ESSAY_SKELETON,
        ESSAY_MILESTONES,
        ESSAY_AI_PROMPTS,
        200,
        who_it_is_for="Students and writers completing course essays, assessments, and timed writing.",
        expected_outcome="A well-structured, citation-ready essay.",
    ),
    # Essay sub-templates
    _academic_base("academic-essay-standard", "Standard Essay", "Classic five-paragraph or multi-paragraph essay.", "academic", "academic-essay", ESSAY_PLANNING, STANDARD_ESSAY_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 201),
    _academic_base("academic-essay-argumentative", "Argumentative Essay", "Make a claim and defend it with evidence. Address counterarguments.", "academic", "academic-essay", ESSAY_PLANNING, ARGUMENTATIVE_ESSAY_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 202),
    _academic_base("academic-essay-persuasive", "Persuasive Essay", "Persuade the reader using ethos, pathos, and logos.", "academic", "academic-essay", ESSAY_PLANNING, PERSUASIVE_ESSAY_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 203),
    _academic_base("academic-essay-analytical", "Analytical Essay", "Analyze a text, concept, or phenomenon. Break it down and interpret.", "academic", "academic-essay", ESSAY_PLANNING, ANALYTICAL_ESSAY_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 204),
    _academic_base("academic-essay-compare-contrast", "Compare and Contrast Essay", "Examine similarities and differences between two subjects.", "academic", "academic-essay", ESSAY_PLANNING, COMPARE_CONTRAST_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 205),
    _academic_base("academic-essay-reflective", "Reflective Essay", "Reflect on experience or learning. Description, analysis, evaluation.", "academic", "academic-essay", ESSAY_PLANNING, REFLECTIVE_ESSAY_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 206),
    _academic_base("academic-essay-expository", "Expository Essay", "Explain a topic clearly and logically. Inform, don't argue.", "academic", "academic-essay", ESSAY_PLANNING, EXPOSITORY_ESSAY_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 207),
    _academic_base("academic-essay-descriptive", "Descriptive Essay", "Describe a subject in vivid detail. Sensory, organized.", "academic", "academic-essay", ESSAY_PLANNING, DESCRIPTIVE_ESSAY_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 208),
    _academic_base("academic-essay-critical-response", "Critical Response Essay", "Respond critically to a text. Summary, analysis, evaluation.", "academic", "academic-essay", ESSAY_PLANNING, CRITICAL_RESPONSE_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 209),
    _academic_base("academic-essay-case-study", "Case Study Essay", "Analyze a case using theory or framework.", "academic", "academic-essay", ESSAY_PLANNING, CASE_STUDY_ESSAY_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 210),
    _academic_base("academic-essay-timed", "Timed Essay Outline", "Quick outline for timed or exam essays. Structure under pressure.", "academic", "academic-essay", ESSAY_PLANNING, TIMED_ESSAY_SKELETON, ESSAY_MILESTONES, ESSAY_AI_PROMPTS, 211),
    # --- RESEARCH (parent) ---
    _academic_base(
        "academic-research",
        "Research & Academic Writing",
        "Research papers, literature reviews, theses, and scholarly articles.",
        "academic",
        None,
        RESEARCH_PLANNING,
        RESEARCH_PAPER_SKELETON,
        RESEARCH_MILESTONES,
        RESEARCH_AI_PROMPTS,
        220,
        who_it_is_for="Researchers, graduate students, and academics.",
        expected_outcome="A publication-ready or submission-ready research document.",
    ),
    _academic_base("academic-research-paper", "Research Paper", "Full IMRaD structure. Abstract, intro, lit review, methods, results, discussion.", "academic", "academic-research", RESEARCH_PLANNING, RESEARCH_PAPER_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 221),
    _academic_base("academic-research-lit-review", "Literature Review", "Synthesize existing research. Thematic organization. Identify gap.", "academic", "academic-research", RESEARCH_PLANNING, LIT_REVIEW_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 222),
    _academic_base("academic-research-annotated-bib", "Annotated Bibliography", "Citations with summaries and evaluations.", "academic", "academic-research", RESEARCH_PLANNING, ANNOTATED_BIB_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 223),
    _academic_base("academic-research-thesis", "Thesis / Dissertation Planning", "Full thesis structure. Chapters, methodology, results, discussion.", "academic", "academic-research", RESEARCH_PLANNING, THESIS_PLANNING_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 224),
    _academic_base("academic-research-capstone", "Capstone Project Report", "Capstone, practicum, or project report. Applied research.", "academic", "academic-research", RESEARCH_PLANNING, CAPSTONE_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 225),
    _academic_base("academic-research-journal", "Journal Article", "Concise format for journal submission.", "academic", "academic-research", RESEARCH_PLANNING, JOURNAL_ARTICLE_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 226),
    _academic_base("academic-research-conference", "Conference Paper", "Short format for conference proceedings.", "academic", "academic-research", RESEARCH_PLANNING, CONFERENCE_PAPER_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 227),
    _academic_base("academic-research-discussion", "Discussion Paper", "Position paper. Argue a stance with evidence.", "academic", "academic-research", RESEARCH_PLANNING, DISCUSSION_PAPER_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 228),
    _academic_base("academic-research-methodology", "Methodology Section Builder", "Standalone methodology section. Design, participants, procedure, ethics.", "academic", "academic-research", RESEARCH_PLANNING, METHODOLOGY_BUILDER_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 229),
    _academic_base("academic-research-results-discussion", "Results/Discussion Structure", "Present findings and interpret. Separate results from discussion.", "academic", "academic-research", RESEARCH_PLANNING, RESULTS_DISCUSSION_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 230),
    _academic_base("academic-research-reference-heavy", "Reference-Heavy Paper", "Heavy engagement with sources. Compare, synthesize, contribute.", "academic", "academic-research", RESEARCH_PLANNING, REFERENCE_HEAVY_SKELETON, RESEARCH_MILESTONES, RESEARCH_AI_PROMPTS, 231),
    # --- COURSE / LECTURE (parent) ---
    _academic_base(
        "academic-course",
        "Course & Lecture Materials",
        "Lecture notes, lesson plans, handouts, and teaching resources.",
        "academic",
        None,
        COURSE_PLANNING,
        LECTURE_NOTES_SKELETON,
        COURSE_MILESTONES,
        COURSE_AI_PROMPTS,
        240,
        who_it_is_for="Educators, lecturers, and instructors.",
        expected_outcome="Course-ready materials with clear structure and learning objectives.",
    ),
    _academic_base("academic-course-lecture-notes", "Lecture Notes", "Structured notes for a lecture. Objectives, content, examples.", "academic", "academic-course", COURSE_PLANNING, LECTURE_NOTES_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 241),
    _academic_base("academic-course-lecture-script", "Lecture Script", "Full script for delivery. Timing. Transitions.", "academic", "academic-course", COURSE_PLANNING, LECTURE_SCRIPT_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 242),
    _academic_base("academic-course-lesson-plan", "Lesson Plan", "Starter, main activity, plenary. Differentiation. Homework.", "academic", "academic-course", COURSE_PLANNING, LESSON_PLAN_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 243),
    _academic_base("academic-course-module", "Course Module Builder", "Multi-week module. Content, activities, assessment.", "academic", "academic-course", COURSE_PLANNING, COURSE_MODULE_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 244),
    _academic_base("academic-course-seminar-handout", "Seminar Handout", "Key points and discussion questions for seminars.", "academic", "academic-course", COURSE_PLANNING, SEMINAR_HANDOUT_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 245),
    _academic_base("academic-course-tutorial", "Tutorial Guide", "Step-by-step tutorial. Objectives, steps, troubleshooting.", "academic", "academic-course", COURSE_PLANNING, TUTORIAL_GUIDE_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 246),
    _academic_base("academic-course-workshop", "Workshop Outline", "Workshop structure. Icebreaker, activities, debrief.", "academic", "academic-course", COURSE_PLANNING, WORKSHOP_OUTLINE_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 247),
    _academic_base("academic-course-workbook", "Course Workbook", "Unit-based workbook. Content, exercises, self-assessment.", "academic", "academic-course", COURSE_PLANNING, COURSE_WORKBOOK_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 248),
    _academic_base("academic-course-reading-response", "Reading Response Template", "Structured response to a reading. Summary, quote, response.", "academic", "academic-course", COURSE_PLANNING, READING_RESPONSE_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 249),
    _academic_base("academic-course-discussion-guide", "Class Discussion Guide", "Discussion questions. Opening, core, probing. Synthesis.", "academic", "academic-course", COURSE_PLANNING, CLASS_DISCUSSION_SKELETON, COURSE_MILESTONES, COURSE_AI_PROMPTS, 250),
    # --- STUDENT SUPPORT (parent) ---
    _academic_base(
        "academic-student",
        "Student Support",
        "Study notes, planners, and revision tools.",
        "academic",
        None,
        STUDENT_PLANNING,
        STUDY_NOTES_SKELETON,
        STUDENT_MILESTONES,
        STUDENT_AI_PROMPTS,
        260,
        who_it_is_for="Students managing assignments and exam prep.",
        expected_outcome="Organized study materials and plans.",
    ),
    _academic_base("academic-student-study-notes", "Study Notes", "Structured notes for revision. Concepts, examples, connections.", "academic", "academic-student", STUDENT_PLANNING, STUDY_NOTES_SKELETON, STUDENT_MILESTONES, STUDENT_AI_PROMPTS, 261),
    _academic_base("academic-student-assignment-planner", "Assignment Planner", "Break down assignments. Schedule. Checkpoints.", "academic", "academic-student", STUDENT_PLANNING, ASSIGNMENT_PLANNER_SKELETON, STUDENT_MILESTONES, STUDENT_AI_PROMPTS, 262),
    _academic_base("academic-student-reading-summary", "Reading Summary", "Summarize readings. Main argument, key points, your notes.", "academic", "academic-student", STUDENT_PLANNING, READING_SUMMARY_SKELETON, STUDENT_MILESTONES, STUDENT_AI_PROMPTS, 263),
    _academic_base("academic-student-source-analysis", "Source Analysis", "Evaluate sources. Authority, purpose, evidence, usefulness.", "academic", "academic-student", STUDENT_PLANNING, SOURCE_ANALYSIS_SKELETON, STUDENT_MILESTONES, STUDENT_AI_PROMPTS, 264),
    _academic_base("academic-student-revision-checklist", "Revision Checklist", "Check thesis, structure, evidence, citations, mechanics.", "academic", "academic-student", STUDENT_PLANNING, REVISION_CHECKLIST_SKELETON, STUDENT_MILESTONES, STUDENT_AI_PROMPTS, 265),
    _academic_base("academic-student-exam-prep", "Exam Prep Outline", "Topic summaries. Practice questions. Weak spots.", "academic", "academic-student", STUDENT_PLANNING, EXAM_PREP_SKELETON, STUDENT_MILESTONES, STUDENT_AI_PROMPTS, 266),
]
