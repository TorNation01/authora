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
from authora.models.notification_delivery_log import NotificationDeliveryLog
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
from authora.models.export_profile import ExportProfile
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
from authora.models.collaboration import (
    ChapterApproval,
    CollaborationActivity,
    ProjectInvite,
    ProjectMember,
    ProjectShare,
)
from authora.models.revision_pass import RevisionChecklistItem, RevisionPass, RevisionPassChapter
from authora.models.reference_item import ReferenceItem
from authora.models.ai_revision import AIRevision
from authora.models.ai_action_log import AIActionLog
from authora.models.ai_action_registry import AIActionRegistry
from authora.models.ghostwriter_session import GhostwriterSession
from authora.models.reminder import Reminder
from authora.models.analytics_event import AnalyticsEvent
from authora.models.publishing_asset import PublishingAsset
from authora.models.feature_flag import FeatureFlag
from authora.models.setup_state import SetupState
from authora.models.plan import Plan
from authora.models.project_template import ProjectTemplate
from authora.models.writing_framework import WritingFramework
from authora.models.subscription import Subscription
from authora.models.usage_record import UsageRecord
from authora.models.entitlement_grant import EntitlementGrant
from authora.models.promo_code import PromoCode, PromoCodeRedemption
from authora.models.entitlement_audit_log import EntitlementAuditLog
from authora.models.content_embedding import ContentEmbedding, IndexingJob
from authora.models.integrity import IntegrityIssue, IntegrityScan, IntegrityScanAnalytics
from authora.models.density import DensityIssue, DensityScan
from authora.models.vault import (
    ChapterCharacterLink,
    ChapterEventLink,
    ChapterLocationLink,
    ChapterResearchLink,
    ChapterSourceLink,
    ChapterThemeLink,
    Idea,
    ResearchEntry,
    Source,
    Theme,
    TimelineEvent,
    VaultCharacter,
    VaultLocation,
    VaultRelationship,
)

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
    "NotificationDeliveryLog",
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
    "ExportProfile",
    "Profile",
    "UserPreference",
    "WritingStyle",
    "BookType",
    "BookSettings",
    "Phase",
    "ChapterSection",
    "ContentHighlight",
    "ContentComment",
    "RevisionPass",
    "RevisionPassChapter",
    "RevisionChecklistItem",
    "ReferenceItem",
    "AIRevision",
    "AIActionLog",
    "AIActionRegistry",
    "GhostwriterSession",
    "Reminder",
    "AnalyticsEvent",
    "PublishingAsset",
    "FeatureFlag",
    "SetupState",
    "Plan",
    "ProjectTemplate",
    "WritingFramework",
    "Subscription",
    "UsageRecord",
    "EntitlementGrant",
    "PromoCode",
    "PromoCodeRedemption",
    "EntitlementAuditLog",
    "ContentEmbedding",
    "IndexingJob",
    "ProjectMember",
    "ProjectInvite",
    "ProjectShare",
    "ChapterApproval",
    "CollaborationActivity",
    "Idea",
    "ResearchEntry",
    "VaultCharacter",
    "VaultLocation",
    "TimelineEvent",
    "VaultRelationship",
    "Theme",
    "Source",
    "ChapterCharacterLink",
    "ChapterLocationLink",
    "ChapterEventLink",
    "ChapterThemeLink",
    "ChapterSourceLink",
    "ChapterResearchLink",
    "IntegrityScan",
    "IntegrityIssue",
    "IntegrityScanAnalytics",
    "DensityScan",
    "DensityIssue",
]
