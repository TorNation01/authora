"""Message libraries: encouragement, recovery nudges, celebration."""

import random
from typing import Sequence

# --- ENCOURAGEMENT MESSAGES ---

ENCOURAGEMENT_MESSAGES: list[str] = [
    "Every word you write is a step forward. You're building something meaningful.",
    "Consistency beats intensity. Small daily steps add up.",
    "The first draft is for you. The rest is for readers. Keep going.",
    "You don't have to be great to start. You have to start to be great.",
    "Your story matters. So does the act of writing it.",
    "One sentence leads to another. Trust the process.",
    "Writers write. You're doing the thing.",
    "The blank page is just a page. Fill it with your voice.",
    "Progress, not perfection. Today's words count.",
    "You showed up. That's the hardest part.",
    "Every chapter you finish is a chapter that didn't exist before.",
    "Your future reader is waiting. Keep going.",
    "Momentum builds. One word at a time.",
    "The middle is messy for everyone. You're not alone.",
    "Your ideas deserve to be written. Give them that.",
    "Small wins compound. Today is a win.",
    "You're not stuck. You're gathering. Keep moving.",
    "The best time to write was yesterday. The second best is now.",
    "Your voice is unique. The world needs it.",
    "Done is better than perfect. Keep drafting.",
]

# --- RECOVERY NUDGES ---

RECOVERY_NUDGES: list[str] = [
    "Life happens. Your goals are still here whenever you're ready. No judgment—just support.",
    "You missed a goal—no worries. Here's a recovery plan to get back on track.",
    "It's okay to take a breath. When you're ready, a small step—even 50 words—can help you find your flow again.",
    "Looks like you might be stuck. Try: open your last chapter and write just one sentence. Momentum often follows.",
    "You haven't written in a while. Next action: open your manuscript and write 100 words. No editing—just momentum.",
    "Welcome back. Your story has been waiting. No need to catch up—just start where you are.",
    "A gentle nudge: your writing space is waiting today. No pressure—just a little reminder.",
    "Every day is a new chance. What's one small thing you can do today?",
    "The page doesn't judge. It's ready when you are.",
    "You've done this before. You can do it again. One word at a time.",
    "Skipped a few days? That's okay. Today is day one again.",
    "Your manuscript doesn't care about the gap. It just wants the next word.",
    "Recovery isn't about catching up. It's about starting again.",
    "Small steps count. Write one paragraph. Or one sentence. Or one word.",
    "The hardest part is opening the file. Do that. See what happens.",
    "You're not behind. You're exactly where you are. Start from here.",
    "Progress isn't linear. A fresh start is still progress.",
    "Your story hasn't gone anywhere. It's right where you left it.",
    "One session can change everything. Give yourself that chance.",
    "No guilt. No shame. Just the next word.",
]

# --- CELEBRATION MESSAGES ---

CELEBRATION_MESSAGES: dict[str, list[str]] = {
    "streak": [
        "You're on a streak! Keep the momentum going.",
        "Another day of showing up. That's how books get written.",
        "Your streak is growing. So is your manuscript.",
        "Consistency champion. Well done.",
        "Day after day. That's the writer's way.",
    ],
    "chapter": [
        "Chapter complete! That's a major milestone.",
        "Another chapter in the books. Literally.",
        "You finished a chapter. Celebrate that.",
        "Chapter done. Your future readers will thank you.",
        "One more chapter. One step closer to 'The End.'",
    ],
    "word_count": [
        "You hit your word count! Today's goal: crushed.",
        "Words on the page. That's what matters.",
        "Your daily target: achieved. Nice work.",
        "Another 500 (or 1000) words. That's real progress.",
        "Word count goal: met. Momentum: building.",
    ],
    "milestone": [
        "Major milestone reached! You're making this happen.",
        "Milestone unlocked. Keep going.",
        "You did it. A significant step toward your goal.",
        "Milestone achieved. Your future self is proud.",
        "That's a big one. Celebrate—then keep writing.",
    ],
    "badge": [
        "Badge earned! You're building a habit that lasts.",
        "New badge unlocked. Your dedication shows.",
        "Achievement unlocked. Well deserved.",
        "You earned this. Wear it proudly.",
        "Another badge. Another proof you're a writer.",
    ],
    "general": [
        "You did it! Take a moment to appreciate your progress.",
        "Well done. Your commitment is paying off.",
        "Celebrate this win. You've earned it.",
        "Progress made. Keep going.",
        "That's the spirit. Onward!",
    ],
}


def get_random_encouragement() -> str:
    """Return a random encouragement message."""
    return random.choice(ENCOURAGEMENT_MESSAGES)


def get_random_recovery_nudge() -> str:
    """Return a random recovery nudge."""
    return random.choice(RECOVERY_NUDGES)


def get_random_celebration(category: str = "general") -> str:
    """Return a random celebration message for the given category."""
    messages = CELEBRATION_MESSAGES.get(category, CELEBRATION_MESSAGES["general"])
    return random.choice(messages)
