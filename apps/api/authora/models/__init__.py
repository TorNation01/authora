"""SQLAlchemy models."""

from authora.models.accountability import (
    AccountabilitySettings,
    ChapterTarget,
    Milestone,
    RecoveryPlan,
    WritingPlan,
)
from authora.models.audit import AuditLog
from authora.models.book import Book, Chapter, ChapterVersion
from authora.models.notification import Notification
from authora.models.gamification import (
    Achievement,
    BadgeDefinition,
    DailyQuest,
    FocusSession,
    Goal,
    PersonalBest,
    StreakLog,
    UserStats,
    WeeklyMission,
)
from authora.models.nonfiction import (
    ArgumentStructure,
    AuthorityBuilder,
    CaseStudy,
    CitationPlaceholder,
    NFChapterPlan,
    NFResearchNote,
    NFWorksheet,
    NonfictionWorkspace,
    StoryInsertion,
    SupportingExample,
    SummaryActionStep,
    TargetAudience,
    TransformationFramework,
)
from authora.models.fiction import (
    CharacterRelationship,
    FictionCharacter,
    FictionChapterPlan,
    FictionTracker,
    FictionWorkspace,
    PlotArc,
    Scene,
    WorldElement,
)
from authora.models.export_job import ExportJob
from authora.models.editing import (
    EditorialAnalysis,
    EditorialJob,
    EditorialSnapshot,
    EditorialSuggestion,
)
from authora.models.ghostwriter import ChapterBrief, GhostwriterWorkspace
from authora.models.journey import JourneyTask, UserJourney
from authora.models.note import Note, NoteAttachment
from authora.models.project import Project
from authora.models.setting import Setting
from authora.models.user import Session, User
from authora.models.profile import Profile
from authora.models.user_preference import UserPreference
from authora.models.writing_style import WritingStyle
from authora.models.book_type import BookType
from authora.models.book_settings import BookSettings
from authora.models.phase import Phase
from authora.models.chapter_section import ChapterSection
from authora.models.content_annotation import ContentHighlight, ContentComment
from authora.models.reference_item import ReferenceItem
from authora.models.ai_revision import AIRevision
from authora.models.ai_action_registry import AIActionRegistry
from authora.models.ghostwriter_session import GhostwriterSession
from authora.models.reminder import Reminder
from authora.models.analytics_event import AnalyticsEvent
from authora.models.publishing_asset import PublishingAsset
from authora.models.feature_flag import FeatureFlag
from authora.models.setup_state import SetupState

__all__ = [
    "AccountabilitySettings",
    "ChapterTarget",
    "Milestone",
    "RecoveryPlan",
    "WritingPlan",
    "User",
    "Session",
    "Project",
    "Book",
    "Chapter",
    "ChapterVersion",
    "Note",
    "NoteAttachment",
    "Notification",
    "UserStats",
    "Achievement",
    "BadgeDefinition",
    "DailyQuest",
    "WeeklyMission",
    "PersonalBest",
    "FocusSession",
    "Goal",
    "StreakLog",
    "AuditLog",
    "Setting",
    "EditorialJob",
    "EditorialAnalysis",
    "EditorialSuggestion",
    "EditorialSnapshot",
    "UserJourney",
    "JourneyTask",
    "FictionWorkspace",
    "FictionCharacter",
    "CharacterRelationship",
    "WorldElement",
    "PlotArc",
    "Scene",
    "FictionTracker",
    "FictionChapterPlan",
    "NonfictionWorkspace",
    "TargetAudience",
    "TransformationFramework",
    "NFChapterPlan",
    "ArgumentStructure",
    "SupportingExample",
    "CaseStudy",
    "StoryInsertion",
    "NFWorksheet",
    "NFResearchNote",
    "CitationPlaceholder",
    "AuthorityBuilder",
    "SummaryActionStep",
    "GhostwriterWorkspace",
    "ChapterBrief",
    "ExportJob",
    "Profile",
    "UserPreference",
    "WritingStyle",
    "BookType",
    "BookSettings",
    "Phase",
    "ChapterSection",
    "ContentHighlight",
    "ContentComment",
    "ReferenceItem",
    "AIRevision",
    "AIActionRegistry",
    "GhostwriterSession",
    "Reminder",
    "AnalyticsEvent",
    "PublishingAsset",
    "FeatureFlag",
    "SetupState",
]
