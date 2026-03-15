/** AI feature explanation copy. Clear, reassuring, jargon-free. */

export const AI_EXPLANATION_COPY: Record<string, string> = {
  ai_overview:
    "AUTHORA's AI helps you write faster without replacing your voice. It can suggest, expand, rewrite, or draft—you stay in control. Use it when you want; ignore it when you don't.",
  ai_rewrite:
    'Rewrites your selection in a different style. Try a new tone, simplify complex sentences, or freshen up the phrasing.',
  ai_expand:
    'Adds detail and depth to your selection. Great for scenes that feel thin or passages that need more development.',
  ai_shorten:
    'Condenses your text while keeping the meaning. Useful for tight prose or cutting word count.',
  ai_improve:
    'Improves clarity and flow. Fixes awkward phrasing and strengthens weak sentences—without changing your voice.',
  ai_fix_grammar:
    'Corrects grammar, punctuation, and common errors. Your voice and meaning stay the same.',
  ai_suggest:
    'Suggests alternative phrasings. Pick one, edit it, or ignore—your choice.',
  ai_continue:
    'Continues writing from your cursor or selection. Use it when you\'re stuck on the next sentence.',
  ai_ghostwriter:
    'Generates a full chapter draft from your outline and brief. Edit, approve, or reject—your story, AI-assisted.',
  ai_api_key:
    'Add your own API key to use AI features. Without a key, some actions may be limited. Keys are stored securely and never shared.',
  ai_privacy:
    'Your text is sent to the AI provider only when you trigger an action. We do not train models on your content.',
};

export function getAIExplanation(key: string): string | undefined {
  return AI_EXPLANATION_COPY[key];
}
