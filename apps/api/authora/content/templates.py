"""Built-in project templates for fiction and nonfiction."""

from typing import Any

# Template IDs for lookup
TEMPLATE_IDS = [
    "romance",
    "thriller",
    "fantasy",
    "mystery",
    "memoir",
    "business",
    "self_help",
    "educational",
    "thought_leadership",
]

# --- FICTION TEMPLATES ---

ROMANCE_TEMPLATE: dict[str, Any] = {
    "id": "romance",
    "name": "Romance Novel",
    "type": "fiction",
    "genre": "Romance",
    "description": "A romance novel with meet-cute, tension, and happily-ever-after",
    "setup_questions": [
        {"id": "meet_cute", "prompt": "How do your leads first meet?", "placeholder": "e.g. mistaken identity, forced proximity, enemies at work"},
        {"id": "internal_conflict", "prompt": "What keeps them apart (internal)?", "placeholder": "fear of commitment, past trauma, career vs love"},
        {"id": "external_conflict", "prompt": "What external force complicates their love?", "placeholder": "family, rival, distance, secret"},
        {"id": "black_moment", "prompt": "What's the darkest moment before the HEA?", "placeholder": "betrayal, misunderstanding, sacrifice"},
        {"id": "tone", "prompt": "Tone: sweet, steamy, or slow-burn?", "placeholder": "sweet / steamy / slow-burn"},
    ],
    "outline": [
        {"title": "Act I: Meet", "summary": "Introduce both leads and the meet-cute"},
        {"title": "Ch 1", "summary": "Lead A's world—establish what they want/need"},
        {"title": "Ch 2", "summary": "Lead B's world—establish their wound or goal"},
        {"title": "Ch 3", "summary": "Meet-cute—sparks fly, but something blocks them"},
        {"title": "Act II: Fall", "summary": "Growing attraction, rising tension, midpoint turn"},
        {"title": "Ch 4", "summary": "Forced together—chemistry builds"},
        {"title": "Ch 5", "summary": "First kiss / first intimacy—relationship deepens"},
        {"title": "Ch 6", "summary": "Midpoint—commitment or revelation changes everything"},
        {"title": "Ch 7", "summary": "External conflict escalates"},
        {"title": "Ch 8", "summary": "Internal conflict peaks—they pull apart"},
        {"title": "Act III: Forever", "summary": "Black moment, grand gesture, HEA"},
        {"title": "Ch 9", "summary": "Black moment—all seems lost"},
        {"title": "Ch 10", "summary": "Grand gesture—one makes the leap"},
        {"title": "Epilogue", "summary": "Happily ever after—glimpse of their future"},
    ],
    "chapter_starters": [
        "She hadn't expected to see him here.",
        "The last person he wanted to run into was her.",
        "Their eyes met across the crowded room.",
        "He'd promised himself he wouldn't call.",
        "She'd built walls for a reason.",
    ],
    "writing_prompts": [
        "Write the moment they first touch (hand, arm, accidental brush).",
        "Write the scene where one admits they've been thinking about the other.",
        "Write the argument that forces them to say what they really feel.",
        "Write the grand gesture—what does your character do to prove their love?",
        "Write the 'I've never felt this way before' confession.",
    ],
    "stuck_prompts": [
        "Skip to the next scene you're excited about. You can bridge later.",
        "Write the scene from the other lead's POV. What are they hiding?",
        "Add a complication: a phone call, an interruption, a secret revealed.",
        "What would make this moment worse for your character? Write that.",
        "Write only the dialogue for the next exchange. Fill in action after.",
    ],
    "accountability_suggestions": [
        "Daily goal: 1 scene or 500 words toward the next beat.",
        "Weekly: Complete one full chapter or two key scenes.",
        "Milestone: Finish Act I (meet-cute through first obstacle) by week 3.",
    ],
    "milestone_map": [
        {"phase": "Setup", "target": "Ch 1-3", "words": 15000, "checkpoint": "Meet-cute complete"},
        {"phase": "Rising", "target": "Ch 4-6", "words": 20000, "checkpoint": "Midpoint turn"},
        {"phase": "Crisis", "target": "Ch 7-8", "words": 15000, "checkpoint": "Black moment"},
        {"phase": "Resolution", "target": "Ch 9-10 + Epilogue", "words": 15000, "checkpoint": "HEA"},
    ],
    "export_presets": {
        "manuscript": {"format": "docx", "include_front_matter": True, "chapter_breaks": True},
        "beta_read": {"format": "docx", "include_front_matter": False, "double_spaced": True},
        "query_package": {"format": "docx", "chapters": "first_three", "synopsis": True},
    },
    "planner_data": {"premise": "", "lead_a": "", "lead_b": "", "trope": "", "heat_level": ""},
}

THRILLER_TEMPLATE: dict[str, Any] = {
    "id": "thriller",
    "name": "Thriller",
    "type": "fiction",
    "genre": "Thriller",
    "description": "High-stakes thriller with ticking clock and moral stakes",
    "setup_questions": [
        {"id": "hook", "prompt": "What's the inciting crime or discovery?", "placeholder": "murder, conspiracy, kidnapping, hack"},
        {"id": "protagonist_stake", "prompt": "Why must your protagonist get involved?", "placeholder": "personal loss, professional duty, accidental witness"},
        {"id": "antagonist", "prompt": "Who or what opposes them? What do they want?", "placeholder": "villain's goal and resources"},
        {"id": "ticking_clock", "prompt": "What's the deadline or escalating threat?", "placeholder": "e.g. next victim in 48 hours"},
        {"id": "twist", "prompt": "What's the midpoint twist?", "placeholder": "ally is enemy, victim is alive, wrong suspect"},
    ],
    "outline": [
        {"title": "Act I: Hook", "summary": "Establish world, inciting incident, protagonist pulled in"},
        {"title": "Ch 1", "summary": "Open with action or discovery—hook immediately"},
        {"title": "Ch 2", "summary": "Introduce protagonist and their normal world"},
        {"title": "Ch 3", "summary": "Inciting incident—they can't look away"},
        {"title": "Act II: Chase", "summary": "Investigation, red herrings, rising danger"},
        {"title": "Ch 4", "summary": "First major clue—wrong direction"},
        {"title": "Ch 5", "summary": "Stakes escalate—someone else at risk"},
        {"title": "Ch 6", "summary": "Midpoint twist—everything changes"},
        {"title": "Ch 7", "summary": "Protagonist in direct danger"},
        {"title": "Ch 8", "summary": "All seems lost—ally betrays or plan fails"},
        {"title": "Act III: Showdown", "summary": "Confrontation, climax, resolution"},
        {"title": "Ch 9", "summary": "Final confrontation—physical and moral"},
        {"title": "Ch 10", "summary": "Aftermath—what's left of the world"},
    ],
    "chapter_starters": [
        "The call came at 3 a.m.",
        "She shouldn't have opened the door.",
        "The body was found in the one place they hadn't looked.",
        "He had twenty-four hours. Maybe less.",
        "The file had been deleted. But not really.",
    ],
    "writing_prompts": [
        "Write the scene where your protagonist realizes they're in over their head.",
        "Write the moment a trusted character reveals they've been lying.",
        "Write the chase—physical or digital. Keep the pace relentless.",
        "Write the villain's POV. What do they want, and why do they believe they're right?",
        "Write the climax—one character must make an impossible choice.",
    ],
    "stuck_prompts": [
        "Add a deadline. What happens if they don't act in the next hour?",
        "Kill a character (or fake it). How does that change the stakes?",
        "Introduce a new clue that contradicts what they thought they knew.",
        "Write the scene where the protagonist is wrong. Dead wrong.",
        "Skip to the explosion. What caused it? Work backward.",
    ],
    "accountability_suggestions": [
        "Daily: 750 words. Thrillers need momentum.",
        "Weekly: One major plot beat (clue, twist, or confrontation).",
        "Milestone: Midpoint twist by week 4—everything after hinges on it.",
    ],
    "milestone_map": [
        {"phase": "Hook", "target": "Ch 1-3", "words": 15000, "checkpoint": "Protagonist committed"},
        {"phase": "Chase", "target": "Ch 4-6", "words": 25000, "checkpoint": "Midpoint twist"},
        {"phase": "Crisis", "target": "Ch 7-8", "words": 15000, "checkpoint": "All is lost"},
        {"phase": "Showdown", "target": "Ch 9-10", "words": 15000, "checkpoint": "Resolution"},
    ],
    "export_presets": {
        "manuscript": {"format": "docx", "include_front_matter": True},
        "pitch": {"format": "docx", "chapters": "first_three", "synopsis": True, "query_letter": True},
    },
    "planner_data": {"premise": "", "protagonist": "", "antagonist": "", "stakes": "", "ticking_clock": ""},
}

FANTASY_TEMPLATE: dict[str, Any] = {
    "id": "fantasy",
    "name": "Fantasy Novel",
    "type": "fiction",
    "genre": "Fantasy",
    "description": "Epic or urban fantasy with magic system and worldbuilding",
    "setup_questions": [
        {"id": "magic_system", "prompt": "How does magic work? What are its limits and costs?", "placeholder": "e.g. elemental, blood, runes, inherited"},
        {"id": "world", "prompt": "What's unique about your world?", "placeholder": "setting, politics, creatures, history"},
        {"id": "protagonist_role", "prompt": "Who is your protagonist in this world?", "placeholder": "chosen one, outsider, reluctant heir"},
        {"id": "antagonist", "prompt": "What force threatens the world or your protagonist?", "placeholder": "dark lord, empire, prophecy, corruption"},
        {"id": "theme", "prompt": "What's the central theme?", "placeholder": "power corrupts, found family, identity"},
    ],
    "outline": [
        {"title": "Act I: Ordinary World", "summary": "Establish world, magic, protagonist before the call"},
        {"title": "Ch 1", "summary": "Open in the world—show, don't tell the rules"},
        {"title": "Ch 2", "summary": "Protagonist's normal life—what they want"},
        {"title": "Ch 3", "summary": "Call to adventure—refusal, then commitment"},
        {"title": "Act II: Journey", "summary": "Trials, allies, enemies, midpoint revelation"},
        {"title": "Ch 4", "summary": "Crossing the threshold—into the wider world"},
        {"title": "Ch 5", "summary": "Tests and allies—build the party"},
        {"title": "Ch 6", "summary": "Midpoint—major revelation about magic, villain, or self"},
        {"title": "Ch 7", "summary": "Approach the inner sanctum—prep for climax"},
        {"title": "Ch 8", "summary": "Ordeal—death and rebirth (literal or figurative)"},
        {"title": "Act III: Return", "summary": "Reward, road back, resurrection, return with elixir"},
        {"title": "Ch 9", "summary": "Final confrontation—magic and character"},
        {"title": "Ch 10", "summary": "Return—world changed, protagonist changed"},
    ],
    "chapter_starters": [
        "The magic had a price. She'd learned that young.",
        "He'd never left the valley. Until now.",
        "The prophecy had gotten it wrong. Or had it?",
        "Three days into the journey, the first thing went wrong.",
        "The old stories never mentioned this part.",
    ],
    "writing_prompts": [
        "Write the first time your protagonist uses magic (or sees it used) in a meaningful way.",
        "Write a scene that shows your world's rules without explaining them.",
        "Write the moment your protagonist meets their mentor or ally.",
        "Write the villain's origin—why did they become this?",
        "Write the climax—magic and choice combined.",
    ],
    "stuck_prompts": [
        "Add a new rule or limit to your magic. How does that complicate the scene?",
        "Write from the POV of a non-human character (creature, spirit, artifact).",
        "Introduce a location you haven't described. What makes it fantastical?",
        "What would your protagonist's mentor say to them right now? Write that conversation.",
        "Skip to the moment of transformation. What changed? Work backward.",
    ],
    "accountability_suggestions": [
        "Daily: 500 words. Worldbuilding counts—notes and scenes.",
        "Weekly: One major scene + one worldbuilding doc.",
        "Milestone: Complete the 'ordinary world' (Ch 1-3) before adding complexity.",
    ],
    "milestone_map": [
        {"phase": "Ordinary World", "target": "Ch 1-3", "words": 20000, "checkpoint": "Call accepted"},
        {"phase": "Journey", "target": "Ch 4-6", "words": 25000, "checkpoint": "Midpoint revelation"},
        {"phase": "Ordeal", "target": "Ch 7-8", "words": 15000, "checkpoint": "Death and rebirth"},
        {"phase": "Return", "target": "Ch 9-10", "words": 15000, "checkpoint": "Elixir brought home"},
    ],
    "export_presets": {
        "manuscript": {"format": "docx", "include_front_matter": True, "map_illustration": True},
        "series_bible": {"format": "docx", "include": "worldbuilding_notes", "character_notes": True},
    },
    "planner_data": {"premise": "", "magic_system": "", "world": "", "protagonist": "", "antagonist": ""},
}

MYSTERY_TEMPLATE: dict[str, Any] = {
    "id": "mystery",
    "name": "Mystery / Whodunit",
    "type": "fiction",
    "genre": "Mystery",
    "description": "Classic mystery with clues, red herrings, and satisfying solution",
    "setup_questions": [
        {"id": "crime", "prompt": "What's the central crime?", "placeholder": "murder, theft, disappearance"},
        {"id": "detective", "prompt": "Who solves it? Professional or amateur?", "placeholder": "detective, journalist, reluctant sleuth"},
        {"id": "suspects", "prompt": "List 3–5 suspects with motive and opportunity", "placeholder": "brief note per suspect"},
        {"id": "clue_philosophy", "prompt": "Fair play or twist? (reader gets same clues / reader is surprised)", "placeholder": "fair play / twist"},
        {"id": "setting", "prompt": "Where does it take place? (closed circle = limited suspects)", "placeholder": "manor, ship, small town"},
    ],
    "outline": [
        {"title": "Act I: Crime & Investigation", "summary": "Crime discovered, detective takes case, suspects introduced"},
        {"title": "Ch 1", "summary": "Crime or discovery—hook the reader"},
        {"title": "Ch 2", "summary": "Detective introduced—why they take the case"},
        {"title": "Ch 3", "summary": "Suspects and alibis—first round of interviews"},
        {"title": "Act II: Clues & Red Herrings", "summary": "Investigation deepens, false leads, midpoint revelation"},
        {"title": "Ch 4", "summary": "First major clue—points wrong way"},
        {"title": "Ch 5", "summary": "Second suspect under focus—also wrong"},
        {"title": "Ch 6", "summary": "Midpoint—key clue that changes the picture"},
        {"title": "Ch 7", "summary": "Danger—detective or ally threatened"},
        {"title": "Ch 8", "summary": "All clues point somewhere—but reader (and detective) may misread"},
        {"title": "Act III: Solution", "summary": "Gathering, reveal, aftermath"},
        {"title": "Ch 9", "summary": "Gathering—detective assembles suspects"},
        {"title": "Ch 10", "summary": "Reveal—whodunit and why. Justice or twist."},
    ],
    "chapter_starters": [
        "The body was found at dawn.",
        "She had lied. He was sure of it.",
        "The alibi didn't hold. Neither did the motive.",
        "Three people had the opportunity. Two had the motive.",
        "The letter had been there all along.",
    ],
    "writing_prompts": [
        "Write the scene where the detective first sees the crime scene. What do they notice?",
        "Write an interview with a suspect who is lying. Plant one tell.",
        "Write the clue that seems to exonerate the killer—but actually implicates them.",
        "Write the gathering—detective lays out the case. Reader (and suspects) follow along.",
        "Write the killer's internal monologue. What do they fear? What do they want?",
    ],
    "stuck_prompts": [
        "Add a new suspect. Give them motive and alibi. Are they red herring or real?",
        "Write the scene where a clue is discovered. Who finds it? What does it seem to mean?",
        "Kill (or threaten) another character. How does that raise stakes?",
        "Write from the killer's POV. What are they doing to avoid detection?",
        "List every clue you've planted. Is the solution fair? Add one more.",
    ],
    "accountability_suggestions": [
        "Daily: 500 words. One scene = one interview, one clue, or one revelation.",
        "Weekly: One full cycle of suspect/clue/reaction.",
        "Milestone: Outline the solution before Act II. You must know whodunit.",
    ],
    "milestone_map": [
        {"phase": "Setup", "target": "Ch 1-3", "words": 15000, "checkpoint": "All suspects introduced"},
        {"phase": "Investigation", "target": "Ch 4-6", "words": 20000, "checkpoint": "Midpoint clue"},
        {"phase": "Deepening", "target": "Ch 7-8", "words": 15000, "checkpoint": "Danger and misdirection"},
        {"phase": "Solution", "target": "Ch 9-10", "words": 15000, "checkpoint": "Reveal complete"},
    ],
    "export_presets": {
        "manuscript": {"format": "docx", "include_front_matter": True},
        "synopsis": {"format": "docx", "synopsis": True, "character_list": True},
    },
    "planner_data": {"premise": "", "detective": "", "crime": "", "suspects": [], "solution": ""},
}

# --- NONFICTION TEMPLATES ---

MEMOIR_TEMPLATE: dict[str, Any] = {
    "id": "memoir",
    "name": "Memoir",
    "type": "nonfiction",
    "genre": "Memoir",
    "description": "Personal story with theme, arc, and universal resonance",
    "setup_questions": [
        {"id": "theme", "prompt": "What's the central theme or question?", "placeholder": "e.g. identity, loss, belonging, resilience"},
        {"id": "timeframe", "prompt": "What period does the memoir cover?", "placeholder": "childhood, a year abroad, a relationship"},
        {"id": "stakes", "prompt": "What was at stake for you?", "placeholder": "survival, belonging, becoming who you are"},
        {"id": "transformation", "prompt": "How did you change by the end?", "placeholder": "what you learned or became"},
        {"id": "voice", "prompt": "Tone: reflective, raw, humorous, lyrical?", "placeholder": "reflective / raw / humorous / lyrical"},
    ],
    "outline": [
        {"title": "Part I: Before", "summary": "Establish the world and the 'before' self"},
        {"title": "Ch 1", "summary": "Opening—drop into a pivotal moment, then step back"},
        {"title": "Ch 2", "summary": "The world you came from—place, family, self"},
        {"title": "Ch 3", "summary": "The inciting change—what disrupted the status quo"},
        {"title": "Part II: During", "summary": "The journey—trials, people, turning points"},
        {"title": "Ch 4", "summary": "First major trial or relationship"},
        {"title": "Ch 5", "summary": "The middle—complications, doubts"},
        {"title": "Ch 6", "summary": "Midpoint—a revelation or loss"},
        {"title": "Ch 7", "summary": "Things get harder before they get better"},
        {"title": "Ch 8", "summary": "The lowest point—crisis of meaning"},
        {"title": "Part III: After", "summary": "Transformation, integration, meaning"},
        {"title": "Ch 9", "summary": "The turn—what changed and why"},
        {"title": "Ch 10", "summary": "Where you are now—reflection and resonance"},
    ],
    "chapter_starters": [
        "I didn't know it then, but that was the last time.",
        "The memory is sharp. The details, less so.",
        "If I could go back, I would tell myself one thing.",
        "The letter arrived on a Tuesday.",
        "We never talked about it. Not then.",
    ],
    "writing_prompts": [
        "Write the scene you've told before. What did you leave out?",
        "Write a letter to your past self at a key moment.",
        "Write the moment you realized something had changed.",
        "Write the scene that still makes you emotional. Don't hold back.",
        "Write what you wish someone had said to you then.",
    ],
    "stuck_prompts": [
        "Write the same scene from another person's perspective. What did they see?",
        "Focus on sensory detail. What did it smell like? Sound like?",
        "Write the version you're afraid to tell. You can revise later.",
        "Skip to the moment of change. What led there?",
        "Write the reflection you'd share with a reader now. What do you understand that you didn't then?",
    ],
    "accountability_suggestions": [
        "Daily: 300–500 words. Memoir is emotionally demanding—pace yourself.",
        "Weekly: One complete chapter or two key scenes.",
        "Milestone: Finish 'Before' (Part I) before diving deep into 'During'.",
    ],
    "milestone_map": [
        {"phase": "Before", "target": "Ch 1-3", "words": 15000, "checkpoint": "World and inciting change"},
        {"phase": "During", "target": "Ch 4-8", "words": 30000, "checkpoint": "Lowest point"},
        {"phase": "After", "target": "Ch 9-10", "words": 10000, "checkpoint": "Transformation and reflection"},
    ],
    "export_presets": {
        "manuscript": {"format": "docx", "include_front_matter": True, "author_note": True},
        "proposal": {"format": "docx", "synopsis": True, "chapter_summaries": True, "market": True},
    },
    "planner_data": {"theme": "", "timeframe": "", "stakes": "", "transformation": "", "voice": ""},
}

BUSINESS_TEMPLATE: dict[str, Any] = {
    "id": "business",
    "name": "Business Book",
    "type": "nonfiction",
    "genre": "Business",
    "description": "Business book with framework, case studies, and actionable takeaways",
    "setup_questions": [
        {"id": "problem", "prompt": "What problem does your book solve?", "placeholder": "e.g. scaling, leadership, strategy"},
        {"id": "audience", "prompt": "Who is your ideal reader?", "placeholder": "founders, managers, executives"},
        {"id": "framework", "prompt": "What's your core framework or method?", "placeholder": "3 steps, 5 pillars, etc."},
        {"id": "proof", "prompt": "What proof do you have? (case studies, data, experience)", "placeholder": "companies, results, years"},
        {"id": "differentiator", "prompt": "How is your approach different?", "placeholder": "what others get wrong"},
    ],
    "outline": [
        {"title": "Introduction", "summary": "Hook, problem, promise, roadmap"},
        {"title": "Part I: The Problem", "summary": "Establish the problem and cost of inaction"},
        {"title": "Ch 1", "summary": "The problem—define it clearly with examples"},
        {"title": "Ch 2", "summary": "Why it persists—what others get wrong"},
        {"title": "Ch 3", "summary": "Cost of inaction—stakes for the reader"},
        {"title": "Part II: The Framework", "summary": "Your method—principles and steps"},
        {"title": "Ch 4", "summary": "Introduce the framework—overview"},
        {"title": "Ch 5", "summary": "Step 1 / Pillar 1—with examples"},
        {"title": "Ch 6", "summary": "Step 2 / Pillar 2—with examples"},
        {"title": "Ch 7", "summary": "Step 3 / Pillar 3—with examples"},
        {"title": "Part III: Implementation", "summary": "How to apply it"},
        {"title": "Ch 8", "summary": "Getting started—first 30/60/90 days"},
        {"title": "Ch 9", "summary": "Pitfalls and how to avoid them"},
        {"title": "Conclusion", "summary": "Recap, call to action, next steps"},
    ],
    "chapter_starters": [
        "The mistake most leaders make is simple.",
        "I've seen this pattern in dozens of companies.",
        "The data tells a different story.",
        "Here's what changed when we applied this.",
        "The first step is counterintuitive.",
    ],
    "writing_prompts": [
        "Write the opening hook—a story or statistic that makes the reader lean in.",
        "Write a case study. Problem, approach, result.",
        "Write the 'why others fail' section. Be specific, not generic.",
        "Write the implementation checklist for one chapter.",
        "Write the conclusion—one clear call to action.",
    ],
    "stuck_prompts": [
        "Add a case study. Real or composite. What happened?",
        "Write the objection a skeptic would raise. Then answer it.",
        "Turn one concept into a diagram or list. Describe it in words first.",
        "Write the 'first 30 days' action plan. Be concrete.",
        "What's the one thing you want readers to do Monday morning? Write that section.",
    ],
    "accountability_suggestions": [
        "Daily: 500 words. One section or one case study.",
        "Weekly: One full chapter with examples.",
        "Milestone: Complete Part I (problem) before Part II (solution).",
    ],
    "milestone_map": [
        {"phase": "Problem", "target": "Intro + Ch 1-3", "words": 15000, "checkpoint": "Problem crystal clear"},
        {"phase": "Framework", "target": "Ch 4-7", "words": 25000, "checkpoint": "Method fully explained"},
        {"phase": "Implementation", "target": "Ch 8-9 + Conclusion", "words": 15000, "checkpoint": "Actionable takeaways"},
    ],
    "export_presets": {
        "manuscript": {"format": "docx", "include_front_matter": True, "toc": True},
        "proposal": {"format": "docx", "synopsis": True, "chapter_summaries": True, "market_analysis": True},
    },
    "planner_data": {"problem": "", "audience": "", "framework": "", "proof": "", "differentiator": ""},
}

SELF_HELP_TEMPLATE: dict[str, Any] = {
    "id": "self_help",
    "name": "Self-Help / Personal Development",
    "type": "nonfiction",
    "genre": "Self-Help",
    "description": "Transformational book with exercises and reader journey",
    "setup_questions": [
        {"id": "transformation", "prompt": "What transformation do you promise?", "placeholder": "e.g. confidence, clarity, habits"},
        {"id": "pain_points", "prompt": "What pain points does your reader have?", "placeholder": "anxiety, procrastination, overwhelm"},
        {"id": "method", "prompt": "What's your method? (steps, framework, practices)", "placeholder": "e.g. 7 habits, 4 pillars"},
        {"id": "credibility", "prompt": "Why are you the one to write this?", "placeholder": "experience, research, results"},
        {"id": "tone", "prompt": "Tone: warm coach, no-nonsense, scientific?", "placeholder": "warm / direct / scientific"},
    ],
    "outline": [
        {"title": "Introduction", "summary": "Hook, reader's pain, promise, how the book works"},
        {"title": "Part I: Awareness", "summary": "Help reader see the problem clearly"},
        {"title": "Ch 1", "summary": "The pattern—what's really going on"},
        {"title": "Ch 2", "summary": "Why we get stuck—psychology or habits"},
        {"title": "Ch 3", "summary": "The cost—what staying stuck means"},
        {"title": "Part II: Shift", "summary": "New perspective, new framework"},
        {"title": "Ch 4", "summary": "Introduce the method—overview"},
        {"title": "Ch 5", "summary": "Principle 1 / Step 1 + exercise"},
        {"title": "Ch 6", "summary": "Principle 2 / Step 2 + exercise"},
        {"title": "Ch 7", "summary": "Principle 3 / Step 3 + exercise"},
        {"title": "Part III: Practice", "summary": "Integration and sustainability"},
        {"title": "Ch 8", "summary": "Daily/weekly practices"},
        {"title": "Ch 9", "summary": "When you slip—compassion and course correction"},
        {"title": "Conclusion", "summary": "Recap, encouragement, next step"},
    ],
    "chapter_starters": [
        "You're not broken. You're just stuck in a pattern.",
        "The first step is noticing.",
        "Here's what the research shows.",
        "Try this. Right now.",
        "The mind resists change. Here's how to work with it.",
    ],
    "writing_prompts": [
        "Write the opening that makes the reader feel seen.",
        "Write an exercise. Clear instructions, 5–10 minutes.",
        "Write the 'why this is hard' section. Validate before you teach.",
        "Write a story from your life that illustrates the principle.",
        "Write the encouragement for when the reader wants to quit.",
    ],
    "stuck_prompts": [
        "Add an exercise. What can the reader do in 10 minutes?",
        "Write the objection: 'But what if I've tried that?' Answer it.",
        "Include a story—yours or a client's. What changed?",
        "Write the 'one thing' takeaway for this chapter.",
        "Add a reflection question. What do you want them to realize?",
    ],
    "accountability_suggestions": [
        "Daily: 400 words. One section + one exercise or story.",
        "Weekly: One chapter with at least one actionable exercise.",
        "Milestone: Complete Part I (awareness) before Part II (shift).",
    ],
    "milestone_map": [
        {"phase": "Awareness", "target": "Intro + Ch 1-3", "words": 12000, "checkpoint": "Reader sees the pattern"},
        {"phase": "Shift", "target": "Ch 4-7", "words": 20000, "checkpoint": "Method and exercises"},
        {"phase": "Practice", "target": "Ch 8-9 + Conclusion", "words": 12000, "checkpoint": "Integration"},
    ],
    "export_presets": {
        "manuscript": {"format": "docx", "include_front_matter": True, "exercises_highlighted": True},
        "workbook": {"format": "docx", "exercises_only": True, "space_for_answers": True},
    },
    "planner_data": {"transformation": "", "pain_points": "", "method": "", "credibility": "", "tone": ""},
}

EDUCATIONAL_TEMPLATE: dict[str, Any] = {
    "id": "educational",
    "name": "Educational / How-To",
    "type": "nonfiction",
    "genre": "Educational",
    "description": "Teach a skill or subject with clear structure and practice",
    "setup_questions": [
        {"id": "topic", "prompt": "What are you teaching?", "placeholder": "e.g. coding, finance, writing"},
        {"id": "prerequisites", "prompt": "What does the reader need to know first?", "placeholder": "beginner / intermediate / advanced"},
        {"id": "outcomes", "prompt": "What will the reader be able to do by the end?", "placeholder": "specific skills or knowledge"},
        {"id": "format", "prompt": "Heavy on exercises, examples, or theory?", "placeholder": "hands-on / conceptual / mixed"},
        {"id": "sequence", "prompt": "What's the logical order of learning?", "placeholder": "foundations first, then build"},
    ],
    "outline": [
        {"title": "Introduction", "summary": "What you'll learn, how to use the book, prerequisites"},
        {"title": "Part I: Foundations", "summary": "Core concepts and vocabulary"},
        {"title": "Ch 1", "summary": "Core concept 1—definitions and basics"},
        {"title": "Ch 2", "summary": "Core concept 2—building blocks"},
        {"title": "Ch 3", "summary": "Core concept 3—how they connect"},
        {"title": "Part II: Skills", "summary": "Step-by-step application"},
        {"title": "Ch 4", "summary": "Skill 1—with examples and practice"},
        {"title": "Ch 5", "summary": "Skill 2—with examples and practice"},
        {"title": "Ch 6", "summary": "Skill 3—with examples and practice"},
        {"title": "Part III: Application", "summary": "Projects and integration"},
        {"title": "Ch 7", "summary": "Project 1—apply what you've learned"},
        {"title": "Ch 8", "summary": "Project 2—deeper application"},
        {"title": "Ch 9", "summary": "Common mistakes and how to avoid them"},
        {"title": "Conclusion", "summary": "Recap, next steps, resources"},
    ],
    "chapter_starters": [
        "Before we dive in, let's clarify one thing.",
        "The key concept here is simple.",
        "Let's walk through an example.",
        "Here's the step-by-step process.",
        "Many beginners make this mistake.",
    ],
    "writing_prompts": [
        "Write the one concept that unlocks the rest. Explain it simply.",
        "Write a worked example. Show every step.",
        "Write a practice exercise. Clear instructions, clear success criteria.",
        "Write the 'common mistake' section. What do learners get wrong?",
        "Write the transition: 'Now that you understand X, we can tackle Y.'",
    ],
    "stuck_prompts": [
        "Add an example. One concrete case from start to finish.",
        "Break down one concept into 3 sub-points. Explain each.",
        "Write a 'try it yourself' exercise. What's the first step?",
        "Add a diagram or list. Describe it in words first.",
        "Write the 'if you get stuck' section. Where do learners typically stall?",
    ],
    "accountability_suggestions": [
        "Daily: 500 words. One section or one example.",
        "Weekly: One chapter with at least one exercise.",
        "Milestone: Complete foundations (Part I) before skills (Part II).",
    ],
    "milestone_map": [
        {"phase": "Foundations", "target": "Intro + Ch 1-3", "words": 15000, "checkpoint": "Core concepts clear"},
        {"phase": "Skills", "target": "Ch 4-6", "words": 18000, "checkpoint": "Skills with practice"},
        {"phase": "Application", "target": "Ch 7-9 + Conclusion", "words": 15000, "checkpoint": "Projects complete"},
    ],
    "export_presets": {
        "manuscript": {"format": "docx", "include_front_matter": True, "code_blocks": True},
        "workbook": {"format": "docx", "exercises_only": True},
    },
    "planner_data": {"topic": "", "prerequisites": "", "outcomes": [], "format": "", "sequence": ""},
}

THOUGHT_LEADERSHIP_TEMPLATE: dict[str, Any] = {
    "id": "thought_leadership",
    "name": "Thought Leadership",
    "type": "nonfiction",
    "genre": "Thought Leadership",
    "description": "Big ideas, vision, and perspective that shifts how people think",
    "setup_questions": [
        {"id": "big_idea", "prompt": "What's the one big idea?", "placeholder": "the contrarian or reframe you're proposing"},
        {"id": "current_belief", "prompt": "What do most people believe that you're challenging?", "placeholder": "the conventional wisdom"},
        {"id": "evidence", "prompt": "What evidence supports your view?", "placeholder": "research, experience, examples"},
        {"id": "implications", "prompt": "What changes if people adopt this view?", "placeholder": "for work, life, society"},
        {"id": "audience", "prompt": "Who needs to hear this?", "placeholder": "leaders, practitioners, policymakers"},
    ],
    "outline": [
        {"title": "Introduction", "summary": "The conventional wisdom, why it's wrong, your reframe"},
        {"title": "Part I: The Case", "summary": "Build the argument"},
        {"title": "Ch 1", "summary": "The problem with how we think now"},
        {"title": "Ch 2", "summary": "Evidence—research, stories, data"},
        {"title": "Ch 3", "summary": "The new framework—your reframe"},
        {"title": "Part II: The Implications", "summary": "What this means in practice"},
        {"title": "Ch 4", "summary": "Implication 1—for individuals or organizations"},
        {"title": "Ch 5", "summary": "Implication 2"},
        {"title": "Ch 6", "summary": "Implication 3"},
        {"title": "Part III: The Future", "summary": "Vision and call to action"},
        {"title": "Ch 7", "summary": "Where this leads—vision"},
        {"title": "Ch 8", "summary": "Objections and responses"},
        {"title": "Conclusion", "summary": "Call to action—what to do differently"},
    ],
    "chapter_starters": [
        "We've been asking the wrong question.",
        "The data suggests something different.",
        "Consider this reframe.",
        "What if the opposite were true?",
        "The future belongs to those who see it first.",
    ],
    "writing_prompts": [
        "Write the opening that states the conventional wisdom—then challenges it.",
        "Write the one statistic or story that proves your point.",
        "Write the reframe in one sentence. Then unpack it.",
        "Write the 'what this means for you' section. Be specific.",
        "Write the call to action. What should the reader do Monday?",
    ],
    "stuck_prompts": [
        "State the strongest objection. Answer it fairly.",
        "Add a case study. Who has done this? What happened?",
        "Write the one-sentence version of your big idea. Then expand.",
        "What would the world look like if everyone believed this? Describe it.",
        "Write the transition to the next chapter. What's the logical next step?",
    ],
    "accountability_suggestions": [
        "Daily: 500 words. One argument, one example, or one implication.",
        "Weekly: One chapter that advances the argument.",
        "Milestone: Complete the case (Part I) before implications (Part II).",
    ],
    "milestone_map": [
        {"phase": "The Case", "target": "Intro + Ch 1-3", "words": 15000, "checkpoint": "Argument clear"},
        {"phase": "Implications", "target": "Ch 4-6", "words": 15000, "checkpoint": "Practical impact"},
        {"phase": "Future", "target": "Ch 7-8 + Conclusion", "words": 12000, "checkpoint": "Call to action"},
    ],
    "export_presets": {
        "manuscript": {"format": "docx", "include_front_matter": True},
        "article_adaptation": {"format": "docx", "chapters": "first_three", "condensed": True},
    },
    "planner_data": {"big_idea": "", "current_belief": "", "evidence": "", "implications": "", "audience": ""},
}

# --- TEMPLATE REGISTRY ---

_TEMPLATES: dict[str, dict[str, Any]] = {
    "romance": ROMANCE_TEMPLATE,
    "thriller": THRILLER_TEMPLATE,
    "fantasy": FANTASY_TEMPLATE,
    "mystery": MYSTERY_TEMPLATE,
    "memoir": MEMOIR_TEMPLATE,
    "business": BUSINESS_TEMPLATE,
    "self_help": SELF_HELP_TEMPLATE,
    "educational": EDUCATIONAL_TEMPLATE,
    "thought_leadership": THOUGHT_LEADERSHIP_TEMPLATE,
}


def get_all_templates() -> list[dict[str, Any]]:
    """Return all built-in templates."""
    return list(_TEMPLATES.values())


def get_template_by_id(template_id: str) -> dict[str, Any] | None:
    """Return template by ID, or None if not found."""
    return _TEMPLATES.get(template_id)


def get_templates_by_type(book_type: str) -> list[dict[str, Any]]:
    """Return templates filtered by fiction or nonfiction."""
    return [t for t in _TEMPLATES.values() if t["type"] == book_type]
