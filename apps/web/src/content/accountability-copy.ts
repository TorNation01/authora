/**
 * Polished user-facing copy for AUTHORA's accountability, reminders, streaks,
 * milestones, and Finish Mode experience.
 *
 * Tone: supportive, motivating, premium, calm. Never guilt-heavy, never childish.
 * Focused on progress and completion.
 */

// --- Page-level ---

export const ACCOUNTABILITY_PAGE = {
  title: 'Progress',
  description: 'Goals that support you—never punish. We adapt to your pace and help you finish.',
  howThisWorksTitle: 'How this works',
  howThisWorksSummary: 'Set goals, get nudges, and track progress. We adapt to your pace—no guilt.',
  suggestedNextStep: 'Suggested next step',
} as const;

// --- Goals section ---

export const GOALS_COPY = {
  heading: 'Goals',
  subheading: 'Set a pace you can actually keep.',
  setPace: 'Set a pace you can actually keep.',
  progressBuilds: 'Progress builds books.',
  smallSessionsCount: 'Small, steady sessions count.',
  dailyGoalPlaceholder: 'e.g. 500',
  weeklyGoalPlaceholder: 'e.g. 3500',
  setDailyGoal: 'Set a daily goal in settings',
  setWeeklyGoal: 'Set a weekly goal in settings',
  ofGoal: (current: number) => `of ${current} goal`,
  presets: {
    gentle: { daily: 250, weekly: 1750, label: 'Gentle' },
    balanced: { daily: 500, weekly: 3500, label: 'Balanced' },
    structured: { daily: 1000, weekly: 7000, label: 'Structured' },
  },
} as const;

// --- Streak section ---

export const STREAK_COPY = {
  heading: 'Streak',
  subheading: 'Keep the momentum alive.',
  keepMomentum: 'Keep the momentum alive.',
  consistencyOverIntensity: 'Consistency matters more than intensity.',
  oneSessionAtATime: 'One session at a time.',
  days: (n: number) => `${n} days`,
  daysOfWriting: (n: number) => `${n} day${n === 1 ? '' : 's'} of writing`,
  keepGoing: 'Keep going.',
} as const;

// --- Milestones ---

export const MILESTONES_COPY = {
  heading: 'Milestones',
  subheading: 'Every finished stage moves the manuscript forward.',
  everyStageMoves: 'Every finished stage moves the manuscript forward.',
  progressDeservesSeen: 'Progress deserves to be seen.',
  oneStepChangesBook: 'One completed step changes the whole book.',
} as const;

// --- Finish Mode (accountability page / settings) ---

export const FINISH_MODE_ACCOUNTABILITY_COPY = {
  heading: 'Finish Mode',
  subheading: 'Done is built one section at a time.',
  doneOneSection: 'Done is built one section at a time.',
  needProgress: 'You do not need perfect. You need progress.',
  finishThenMove: 'Finish this stage, then keep moving.',
  momentumCreates: 'Momentum creates books.',
  oneFinishedBeatsTen: 'One finished chapter beats ten unfinished ideas.',
  justFinish: 'Just finish',
  today: 'Today',
  daysLeft: (n: number) => `${n} days left`,
  wordsPerDay: (n: number) => `~${n}w/day`,
  enterFinishMode: 'Enter Finish Mode',
  exitFinishMode: 'Exit',
  suggestedNextStep: 'Suggested next step',
} as const;

// --- Nudges (for reminders, dashboard, empty states) ---

export const NUDGES_COPY = {
  smallSessionKeepsAlive: 'A small session today keeps the book alive.',
  pickUpWhereLeftOff: 'Pick up where you left off.',
  bookStillWaiting: 'Your book is still waiting for you.',
  keepDraftMoving: 'Keep the draft moving.',
  fifteenMinutesCounts: 'Even fifteen minutes counts.',
} as const;

// --- Recovery plans ---

export const RECOVERY_COPY = {
  heading: 'Recovery plans',
  subheading: 'Life happens. Here are gentle plans to help you get back on track—no judgment.',
  gotIt: 'Got it',
  suggestedWordsPerDay: (n: number) => `Suggested: ${n} words/day`,
} as const;

// --- Reminders & settings ---

export const REMINDERS_COPY = {
  heading: 'Reminders & encouragement',
  subheading: 'Choose how we support you. Your style shapes our reminders and recovery plans.',
  howWeEncourage: 'How we encourage you',
  enableReminders: 'Enable reminders (opt-in)',
  emailReminders: 'Email reminders',
  reminderConsent:
    'Reminders are opt-in. By enabling email reminders, you consent to receive supportive nudges at your configured times. You can disable either at any time.',
  reminderTimesLabel: 'Reminder times (your timezone)',
  reminderTimesHint: 'e.g. 09:00, 14:00. We send at these times in your timezone.',
  quietHours: 'No reminders during quiet hours (e.g. 22:00–07:00).',
  reminderCadence: 'Reminder cadence',
  reminderTypes: 'Reminder types',
  reminderTypesHint: 'Choose which reminders you want. Leave all checked for full support.',
  sendTest: 'Send test notification',
  sendTestHint: 'Sends in-app and email (if enabled) to verify your settings.',
  pausePlan: 'Pause plan',
  resumePlan: 'Resume plan',
  remindersPaused: 'Reminders paused',
} as const;

// --- Encouragement styles (for settings) ---

export const ENCOURAGEMENT_STYLES = [
  { value: 'gentle', label: 'Gentle', desc: 'Soft nudges, no pressure' },
  { value: 'balanced', label: 'Balanced', desc: 'Supportive check-ins' },
  { value: 'firm', label: 'Firm', desc: 'Clear expectations' },
  { value: 'coach', label: 'Coach', desc: 'Motivating and strategic' },
  { value: 'structured', label: 'Structured', desc: 'Schedules and milestones' },
] as const;
