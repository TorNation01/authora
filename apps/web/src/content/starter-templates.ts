/**
 * Premium starter templates for AUTHORA.
 * Each starter maps to a backend template slug and includes UX metadata.
 */

export type GuidanceLevel = 'guided' | 'flexible' | 'freeform';

export interface StarterTemplate {
  id: string;
  slug: string;
  name: string;
  shortDescription: string;
  /** Who this starter is for */
  whoItIsFor: string;
  /** How guided: guided (full structure), flexible (lighter), freeform (minimal) */
  guidanceLevel: GuidanceLevel;
  guidanceDescription: string;
  /** Backend template slug to resolve to template_id */
  templateSlug: string | null;
  /** Knowledge mode for workspace modules */
  knowledgeMode: 'fiction' | 'nonfiction' | 'memoir' | 'workbook' | 'hybrid';
  /** Suggested export formats */
  suggestedExports: string[];
  /** AI assist default prompts (labels for UI) */
  aiAssistDefaults: string[];
  /** Accountability suggestions (short labels) */
  accountabilitySuggestions: string[];
  /** Group for display */
  group: 'fiction' | 'nonfiction' | 'other';
}

export const STARTER_TEMPLATES: StarterTemplate[] = [
  // --- FICTION ---
  {
    id: 'fiction-novel',
    slug: 'fiction-novel',
    name: 'Fiction Novel',
    shortDescription: 'Build stories with structure, character, tension, and momentum.',
    whoItIsFor: 'Fiction writers of any genre who want a structured approach without losing creative freedom.',
    guidanceLevel: 'guided',
    guidanceDescription: 'Full three-act structure, chapter skeletons, and planning prompts.',
    templateSlug: 'fiction',
    knowledgeMode: 'fiction',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Brainstorm plot twists', 'Deepen character motivation', 'Write scenes with emotion'],
    accountabilitySuggestions: ['Weekly word goals', 'Act-by-act milestones', 'Beta reader checkpoints'],
    group: 'fiction',
  },
  {
    id: 'romance-novel',
    slug: 'romance-novel',
    name: 'Romance Novel',
    shortDescription: 'Meet-cute, tension, and happily-ever-after.',
    whoItIsFor: 'Romance writers who want structure that delivers the emotional payoff readers expect.',
    guidanceLevel: 'guided',
    guidanceDescription: 'Romance beat structure, chemistry prompts, and HEA roadmap.',
    templateSlug: 'fiction-romance',
    knowledgeMode: 'fiction',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Brainstorm romantic tension', 'Write chemistry without being explicit', 'Craft satisfying HEA'],
    accountabilitySuggestions: ['Romance beat milestones', 'Weekly scene goals', 'Chemistry pass checkpoint'],
    group: 'fiction',
  },
  {
    id: 'fantasy-speculative',
    slug: 'fantasy-speculative',
    name: 'Fantasy / Speculative',
    shortDescription: 'Epic or contemporary fantasy with worldbuilding and magic systems.',
    whoItIsFor: 'Fantasy and speculative fiction writers who want to balance worldbuilding with plot and character.',
    guidanceLevel: 'guided',
    guidanceDescription: "Hero's journey structure, worldbuilding modules, and magic system planning.",
    templateSlug: 'fiction-fantasy',
    knowledgeMode: 'fiction',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Develop magic system rules', 'Write worldbuilding scenes', 'Check consistency'],
    accountabilitySuggestions: ['World & magic defined', 'Act milestones', 'Consistency pass'],
    group: 'fiction',
  },
  {
    id: 'thriller-mystery',
    slug: 'thriller-mystery',
    name: 'Thriller / Mystery',
    shortDescription: 'Suspense-driven plot with clues, twists, and pacing.',
    whoItIsFor: 'Thriller and mystery writers who want structure that delivers tension and payoff.',
    guidanceLevel: 'guided',
    guidanceDescription: 'Clue map, red herrings, twist planning, and pacing structure.',
    templateSlug: 'fiction-thriller',
    knowledgeMode: 'fiction',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Plant subtle clues', 'Raise tension', 'Make twists feel inevitable'],
    accountabilitySuggestions: ['Clue map complete', 'Act milestones', 'Pacing pass'],
    group: 'fiction',
  },
  {
    id: 'literary-fiction',
    slug: 'literary-fiction',
    name: 'Literary Fiction',
    shortDescription: 'Character-driven literary fiction with emotional depth.',
    whoItIsFor: 'Literary fiction writers who want structure that supports voice and theme without feeling formulaic.',
    guidanceLevel: 'flexible',
    guidanceDescription: 'Lighter structure with emphasis on character arc and thematic resonance.',
    templateSlug: 'fiction-literary',
    knowledgeMode: 'fiction',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Deepen character interiority', 'Explore theme through scene', 'Refine prose'],
    accountabilitySuggestions: ['Character arc milestones', 'Weekly writing goals', 'Voice consistency pass'],
    group: 'fiction',
  },
  // --- NONFICTION ---
  {
    id: 'memoir',
    slug: 'memoir',
    name: 'Memoir',
    shortDescription: 'Shape lived experience into a story with meaning and reflection.',
    whoItIsFor: 'Writers sharing their life story with meaning and structure.',
    guidanceLevel: 'guided',
    guidanceDescription: 'Emotional arc structure, timeline mapping, and sensitivity notes.',
    templateSlug: 'memoir',
    knowledgeMode: 'memoir',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Turn memory into scene', 'Articulate lessons', 'Deepen emotional resonance'],
    accountabilitySuggestions: ['Timeline mapped', 'Themes identified', 'Sensitivity review'],
    group: 'nonfiction',
  },
  {
    id: 'personal-story',
    slug: 'personal-story',
    name: 'Personal Story / Life Lessons',
    shortDescription: 'Share your story and the lessons that shaped you.',
    whoItIsFor: 'Writers who want to share personal experiences and life lessons without a full memoir structure.',
    guidanceLevel: 'flexible',
    guidanceDescription: 'Theme-based structure with reflection prompts and story grouping.',
    templateSlug: 'nonfiction-personal-story',
    knowledgeMode: 'memoir',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Shape story into lesson', 'Add reflection', 'Find thematic threads'],
    accountabilitySuggestions: ['Stories collected', 'Lessons outlined', 'Weekly reflection goals'],
    group: 'nonfiction',
  },
  {
    id: 'business-authority',
    slug: 'business-authority',
    name: 'Business / Authority Book',
    shortDescription: 'Establish expertise and deliver actionable insights.',
    whoItIsFor: 'Executives, consultants, and experts who want to position themselves as authorities.',
    guidanceLevel: 'guided',
    guidanceDescription: 'Authority structure, case studies, and positioning framework.',
    templateSlug: 'nonfiction-business',
    knowledgeMode: 'nonfiction',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Outline chapters', 'Suggest case studies', 'Write strong CTAs'],
    accountabilitySuggestions: ['Positioning defined', 'Chapter outline', 'Expert review checkpoint'],
    group: 'nonfiction',
  },
  {
    id: 'how-to-nonfiction',
    slug: 'how-to-nonfiction',
    name: 'How-to Non-fiction',
    shortDescription: 'Step-by-step instructional guide that teaches a skill.',
    whoItIsFor: 'Experts and educators who want to create clear, actionable how-to content.',
    guidanceLevel: 'guided',
    guidanceDescription: 'Instructional structure with steps, examples, and exercises.',
    templateSlug: 'nonfiction-howto',
    knowledgeMode: 'nonfiction',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Outline steps', 'Add examples', 'Write exercises'],
    accountabilitySuggestions: ['Steps defined', 'Examples added', 'Beta tester feedback'],
    group: 'nonfiction',
  },
  {
    id: 'self-help',
    slug: 'self-help',
    name: 'Self-help',
    shortDescription: 'Transformational book that takes readers from problem to solution.',
    whoItIsFor: 'Coaches, experts, and thought leaders who want to help readers change their lives.',
    guidanceLevel: 'guided',
    guidanceDescription: 'Problem-solution-result structure with stories and exercises.',
    templateSlug: 'nonfiction-selfhelp',
    knowledgeMode: 'nonfiction',
    suggestedExports: ['docx', 'epub', 'pdf'],
    aiAssistDefaults: ['Outline chapters', 'Suggest stories', 'Write exercises and CTAs'],
    accountabilitySuggestions: ['Problem defined', 'Framework outlined', 'Stories added'],
    group: 'nonfiction',
  },
  {
    id: 'workbook',
    slug: 'workbook',
    name: 'Workbook',
    shortDescription: 'Guided content with prompts, exercises, and action-oriented structure.',
    whoItIsFor: 'Coaches, educators, and facilitators creating hands-on learning experiences.',
    guidanceLevel: 'guided',
    guidanceDescription: 'Module-exercise structure with prompts and worksheets.',
    templateSlug: 'workbook',
    knowledgeMode: 'workbook',
    suggestedExports: ['docx', 'pdf'],
    aiAssistDefaults: ['Write reflection prompts', 'Suggest exercises', 'Design worksheets'],
    accountabilitySuggestions: ['Outcomes defined', 'Modules drafted', 'Beta test complete'],
    group: 'nonfiction',
  },
  {
    id: 'guided-journal',
    slug: 'guided-journal',
    name: 'Guided Journal',
    shortDescription: 'Design reflective writing experiences with prompts and themes.',
    whoItIsFor: 'Writers creating guided journals for readers to work through.',
    guidanceLevel: 'flexible',
    guidanceDescription: 'Prompt bank, entry structure, and themed sections.',
    templateSlug: 'journal',
    knowledgeMode: 'workbook',
    suggestedExports: ['pdf', 'docx'],
    aiAssistDefaults: ['Suggest daily prompts', 'Create themed sections', 'Design entry structure'],
    accountabilitySuggestions: ['Prompt bank complete', 'Structure defined', 'Sample entries drafted'],
    group: 'nonfiction',
  },
  // --- OTHER ---
  {
    id: 'ghostwritten',
    slug: 'ghostwritten',
    name: 'Ghostwritten Book',
    shortDescription: "Capture a client's message, voice, and source material.",
    whoItIsFor: 'Ghostwriters managing client projects professionally.',
    guidanceLevel: 'guided',
    guidanceDescription: 'Client workflow, voice capture, and approval stages.',
    templateSlug: 'ghostwritten-book',
    knowledgeMode: 'hybrid',
    suggestedExports: ['docx', 'pdf'],
    aiAssistDefaults: ['Match client voice', 'Structure interviews', 'Track revisions'],
    accountabilitySuggestions: ['Intake complete', 'Outline approved', 'Revision rounds'],
    group: 'other',
  },
  {
    id: 'blank',
    slug: 'blank',
    name: 'Blank Project',
    shortDescription: 'Start from scratch with full creative control.',
    whoItIsFor: 'Writers who prefer no template constraints and want to build structure as they go.',
    guidanceLevel: 'freeform',
    guidanceDescription: 'Minimal structure. Add chapters and planning as you need them.',
    templateSlug: null,
    knowledgeMode: 'fiction',
    suggestedExports: ['docx', 'pdf', 'epub', 'txt'],
    aiAssistDefaults: [],
    accountabilitySuggestions: ['Custom milestones', 'Your own goals'],
    group: 'other',
  },
];

export const STARTER_GROUPS = {
  fiction: 'Fiction',
  nonfiction: 'Non-fiction',
  other: 'Other',
} as const;

export const GUIDANCE_LABELS: Record<GuidanceLevel, string> = {
  guided: 'Full guidance',
  flexible: 'Flexible',
  freeform: 'Freeform',
};
