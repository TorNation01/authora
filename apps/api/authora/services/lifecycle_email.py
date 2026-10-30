"""Lifecycle email: the seven-message ladder from signup to first published book.

Authora already sends a welcome email the moment an account exists, and then
goes quiet until the customer pays us or publishes. That leaves the whole
middle — starting a book, building the bible, writing the first chapter,
getting to a finished draft, exporting — with no message at all, which is
where trials quietly expire.

This module owns the sequence. Design rules:

* **Seven messages, in order, once each.** ``LIFECYCLE_STEPS`` is the whole
  sequence; the ledger table (``lifecycle_email_log``) is the guarantee a step
  is never sent twice, keyed on (user_id, step).
* **Time opens the gate, the customer's actual state decides the message.** A
  step becomes *due* when its delay has elapsed; if the customer has already
  moved past that point the step is recorded as ``skipped`` rather than sent
  stale advice ("start your first book" to somebody with three books is worse
  than silence).
* **One email per user per run**, so a sweep can never produce a burst of five
  messages to one inbox.
* **The last message is an event, not a timer**: it fires when the first
  manuscript is handed to a publisher, which ends the ladder.
* A failed send is logged and retried on the next run; a skipped step is
  terminal.

The sweep is called from ``POST /api/v1/accountability/cron/lifecycle-emails``
(cron, X-Cron-Secret), and gated by ``lifecycle_emails_enabled`` so a deploy
does not mail the existing customer base until the operator turns it on.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Collection, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    Book,
    BookBible,
    Chapter,
    ExportJob,
    LifecycleEmailLog,
    Project,
    PublisherSubmission,
    User,
)
from authora.services.transactional_email import _button, _layout, app_url, support_email

logger = logging.getLogger(__name__)

SENT = "sent"
SKIPPED = "skipped"
FAILED = "failed"

#: statuses that close a step permanently. ``failed`` is deliberately absent:
#: a bounced or refused send must be retried on the next sweep.
CLOSED = (SENT, SKIPPED)

MAX_WORDS_FOR_NO_EXPORT = 15000


# --------------------------------------------------------------------------
# progress: what the customer has actually done
# --------------------------------------------------------------------------
@dataclass
class UserProgress:
    projects: int = 0
    books: int = 0
    bibles: int = 0
    chapters: int = 0
    words: int = 0
    exports: int = 0
    published: int = 0
    book_title: str | None = None

    @property
    def started(self) -> bool:
        return self.projects > 0


def count_words(node: Any) -> int:
    """Count words in a ProseMirror document.

    Chapter prose is stored as ProseMirror JSON, not a string, so the word
    count is the sum of the ``text`` leaves — the same rule the editor uses.
    """
    if isinstance(node, str):
        return len(node.split())
    if isinstance(node, list):
        return sum(count_words(n) for n in node)
    if isinstance(node, dict):
        text = node.get("text")
        if isinstance(text, str):
            return len(text.split())
        total = 0
        for key in ("content", "doc", "children"):
            if key in node:
                total += count_words(node[key])
        return total
    return 0


async def collect_progress(db: AsyncSession, user_id: UUID) -> UserProgress:
    p = UserProgress()

    p.projects = (
        await db.execute(
            select(func.count(Project.id)).where(Project.user_id == user_id, Project.deleted_at.is_(None))
        )
    ).scalar_one() or 0

    book_ids = (
        await db.execute(
            select(Book.id)
            .join(Project, Project.id == Book.project_id)
            .where(Project.user_id == user_id, Project.deleted_at.is_(None), Book.deleted_at.is_(None))
        )
    ).scalars().all()
    p.books = len(book_ids)
    if not book_ids:
        return p

    p.book_title = (
        await db.execute(select(Book.title).where(Book.id.in_(book_ids)).order_by(Book.created_at))
    ).scalars().first()

    p.bibles = (
        await db.execute(select(func.count(BookBible.id)).where(BookBible.book_id.in_(book_ids)))
    ).scalar_one() or 0

    chapters = (
        await db.execute(select(Chapter.content).where(Chapter.book_id.in_(book_ids)))
    ).scalars().all()
    counts = [count_words(c) for c in chapters if c]
    p.chapters = sum(1 for c in counts if c > 0)
    p.words = sum(counts)

    p.exports = (
        await db.execute(select(func.count(ExportJob.id)).where(ExportJob.user_id == user_id))
    ).scalar_one() or 0

    p.published = (
        await db.execute(
            select(func.count(PublisherSubmission.id)).where(PublisherSubmission.user_id == user_id)
        )
    ).scalar_one() or 0

    return p


# --------------------------------------------------------------------------
# the seven steps
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class LifecycleStep:
    key: str
    delay_hours: int
    subject: str
    heading: str
    when: Callable[[UserProgress], bool]
    build: Callable[[UserProgress, str], tuple[str, str]]  # (text, html body)
    #: event-driven steps are invisible until their condition is true — they are
    #: never recorded as "skipped" for customers who have not reached them yet.
    event: bool = False


@dataclass(frozen=True)
class Context:
    name: str
    progress: UserProgress


def _greeting(name: str) -> str:
    return name.strip() or "there"


def _book_label(p: UserProgress) -> str:
    return p.book_title or "your book"


def _b1(p: UserProgress, name: str) -> tuple[str, str]:
    text = f"""Hi {name},

Your Authora account is ready. Everything below is in the app already; nothing else is required to begin.

1. Open your dashboard: {app_url('/dashboard')}
2. Choose Start a book. Pick a template, or begin from your own premise.
3. Answer the short brief — genre, audience, length. Authora turns that into a book idea, a Book Bible, an outline and chapter briefs.
4. Write in the editor. Autosave keeps a local copy as well as the saved version.
5. Export when you are ready: DOCX, EPUB, PDF, TXT, Markdown, HTML, JSON.
6. When the manuscript is finished, use Publish & release to send it to Anema House Publishing. You get a reference number back.

Your plan and billing live here: {app_url('/dashboard/billing')}
Common questions: {app_url('/help')}
Contact us: {app_url('/contact')} or {support_email()}
"""
    html = _layout(
        "Your book starts here",
        f"""<p style="margin:0 0 14px 0;">Hi {name},</p>
        <p style="margin:0 0 14px 0;">Your account is ready. Here is the whole path, start to finish.</p>
        <ol style="margin:0 0 6px 18px;padding:0;">
          <li style="margin-bottom:8px;"><strong>Start a book.</strong> Pick a template, or begin from your own premise.</li>
          <li style="margin-bottom:8px;"><strong>Answer the brief.</strong> Authora builds the idea, the Book Bible and the chapter briefs.</li>
          <li style="margin-bottom:8px;"><strong>Write.</strong> Autosave keeps a local copy as well as the saved version.</li>
          <li><strong>Publish.</strong> Publish &amp; release hands the manuscript to Anema House Publishing.</li>
        </ol>
        {_button("Open my dashboard", app_url('/dashboard'))}
        <p style="margin:0;color:#8b909a;font-size:13px;">A person reads every reply: {support_email()}</p>""",
    )
    return text, html


def _b2(p: UserProgress, name: str) -> tuple[str, str]:
    text = f"""Hi {name},

Yesterday you created an Authora account. The blank page is still the only hard part, and it does not have to be blank.

Start a book and answer four questions — genre, audience, length, and what the story is about. Authora turns those into a book idea, a Book Bible (premise, characters, world, voice) and a chapter-by-chapter outline. You will have a first chapter brief in front of you in a few minutes, not a research project.

Start here: {app_url('/dashboard')}

If something is unclear or in your way, reply to this email and a person answers.

— Authora
"""
    html = _layout(
        "Start your first book",
        f"""<p style="margin:0 0 14px 0;">Hi {name},</p>
        <p style="margin:0 0 14px 0;">Yesterday you created an account. The blank page is still the only hard part — and it does not have to be blank.</p>
        <p style="margin:0 0 4px 0;">Answer four questions (genre, audience, length, premise) and Authora builds the idea, the Book Bible and the outline. You end up with a first chapter brief, not a research project.</p>
        {_button("Start my first book", app_url('/dashboard'))}
        <p style="margin:0;color:#8b909a;font-size:13px;">Stuck on anything? Reply to this email — a person answers.</p>""",
    )
    return text, html


def _b3(p: UserProgress, name: str) -> tuple[str, str]:
    title = _book_label(p)
    text = f"""Hi {name},

{title} exists, and that is the hardest click done. The next step is the one that decides whether the book holds together: the Book Bible.

In the book, open Book Bible and fill the story foundation — premise, protagonist, what they want, what is in the way, and how it ends. Everything downstream reads from those answers: the outline, the chapter briefs, the ghostwriter.

Open the bible: {app_url('/dashboard')}

Ten minutes there saves a rewrite later.

— Authora
"""
    html = _layout(
        "Build the Book Bible",
        f"""<p style="margin:0 0 14px 0;">Hi {name},</p>
        <p style="margin:0 0 14px 0;"><strong>{title}</strong> exists — that is the hardest click done. The next step decides whether the book holds together: the Book Bible.</p>
        <p style="margin:0 0 4px 0;">Fill the story foundation — premise, protagonist, what they want, what is in the way, how it ends. The outline, the chapter briefs and the ghostwriter all read from those answers.</p>
        {_button("Open the Book Bible", app_url('/dashboard'))}
        <p style="margin:0;color:#8b909a;font-size:13px;">Ten minutes there saves a rewrite later.</p>""",
    )
    return text, html


def _b4(p: UserProgress, name: str) -> tuple[str, str]:
    title = _book_label(p)
    text = f"""Hi {name},

{title} has structure but no prose yet. The first chapter is the one that teaches you the app, and it is smaller than it looks.

Open the book, pick Chapter 1, and write the first paragraph — badly is fine. Autosave keeps your words as you go, and the brief beside you already lists what the chapter has to do.

Write here: {app_url('/dashboard')}

Reply if you would rather have us look at the chapter with you.

— Authora
"""
    html = _layout(
        "Write the first chapter",
        f"""<p style="margin:0 0 14px 0;">Hi {name},</p>
        <p style="margin:0 0 14px 0;"><strong>{title}</strong> has structure but no prose yet. The first chapter is the one that teaches you the app — and it is smaller than it looks.</p>
        <p style="margin:0 0 4px 0;">Open Chapter 1 and write the first paragraph. Badly is fine. Autosave keeps every word, and the brief beside the editor already lists what the chapter has to do.</p>
        {_button("Write the first chapter", app_url('/dashboard'))}
        <p style="margin:0;color:#8b909a;font-size:13px;">Would you rather we read it with you? Reply and ask.</p>""",
    )
    return text, html


def _b5(p: UserProgress, name: str) -> tuple[str, str]:
    title = _book_label(p)
    text = f"""Hi {name},

You have {p.words:,} words of {title} saved. That is no longer an experiment — it is a draft in progress, and the only thing that kills one is a gap of a week.

Two things that keep the pace:
- Set a daily target in the app; the dashboard tracks it and the streak with it.
- Write the next chapter brief before you stop for the day, so tomorrow starts with a decision already made, not a blank page.

Continue: {app_url('/dashboard')}

— Authora
"""
    html = _layout(
        "Keep the draft moving",
        f"""<p style="margin:0 0 14px 0;">Hi {name},</p>
        <p style="margin:0 0 14px 0;"><strong>{p.words:,} words</strong> of <strong>{title}</strong> saved. That is not an experiment any more — it is a draft, and the only thing that reliably kills one is a week of silence.</p>
        <ul style="margin:0 0 4px 18px;padding:0;">
          <li style="margin-bottom:8px;">Set a daily target — the dashboard tracks it, and the streak with it.</li>
          <li>Write tomorrow's chapter brief before you stop, so the next session starts with a decision instead of a blank page.</li>
        </ul>
        {_button("Continue writing", app_url('/dashboard'))}""",
    )
    return text, html


def _b6(p: UserProgress, name: str) -> tuple[str, str]:
    title = _book_label(p)
    text = f"""Hi {name},

{title} is {p.words:,} words deep, and you have not exported it yet. An unexported manuscript lives in one place; an exported one is yours wherever you go.

Export takes one click and gives you DOCX, EPUB, PDF, TXT, Markdown, HTML or JSON — the same text, laid out for whatever you do next (beta readers, an editor, print, or the publishing house).

Export now: {app_url('/dashboard/export')}

When it is ready for a publisher, Publish & release sends the pack to Anema House Publishing and returns a reference number.

— Authora
"""
    html = _layout(
        "Your manuscript is ready to export",
        f"""<p style="margin:0 0 14px 0;">Hi {name},</p>
        <p style="margin:0 0 14px 0;"><strong>{title}</strong> is <strong>{p.words:,} words</strong> deep and has never been exported. An unexported manuscript lives in one place; an exported one is yours wherever you go.</p>
        <p style="margin:0 0 4px 0;">One click gives you DOCX, EPUB, PDF, TXT, Markdown, HTML or JSON — for beta readers, an editor, print, or the house.</p>
        {_button("Export my manuscript", app_url('/dashboard/export'))}
        <p style="margin:0;color:#8b909a;font-size:13px;">Ready for a publisher? Publish &amp; release sends the pack to Anema House and returns a reference number.</p>""",
    )
    return text, html


def _b7(p: UserProgress, name: str) -> tuple[str, str]:
    title = _book_label(p)
    text = f"""Hi {name},

{title} is out of your hands and in front of a publisher. That is the last step of this sequence and the first step of the next thing: the book now has readers on the other side of it.

What happens from here:
- Anema House reads the pack you sent — manuscript, blurb, synopsis, front matter.
- You can check the status any time from the book's Publish & release page.
- A decision usually arrives within four to six weeks. Silence is not a rejection; it means it is still in the queue.

Check the submission: {app_url('/dashboard/export')}

While you wait, start the next book — the second one is always easier than the first.

— Authora
"""
    html = _layout(
        "Your first book is out",
        f"""<p style="margin:0 0 14px 0;">Hi {name},</p>
        <p style="margin:0 0 14px 0;"><strong>{title}</strong> is out of your hands and in front of a publisher. That is the last message in this sequence and the first step of the next thing.</p>
        <ul style="margin:0 0 4px 18px;padding:0;">
          <li style="margin-bottom:8px;">Anema House reads the pack you sent — manuscript, blurb, synopsis, front matter.</li>
          <li style="margin-bottom:8px;">Status is on the book's Publish &amp; release page, any time.</li>
          <li>A decision usually arrives in four to six weeks. Silence is the queue, not a rejection.</li>
        </ul>
        {_button("Check the submission", app_url('/dashboard/export'))}
        <p style="margin:0;color:#8b909a;font-size:13px;">While you wait, start the next book. The second one is always easier.</p>""",
    )
    return text, html


LIFECYCLE_STEPS: tuple[LifecycleStep, ...] = (
    LifecycleStep("welcome", 0, "Welcome to Authora — here is how to start your book", "Your book starts here", lambda p: True, _b1),
    LifecycleStep("first_book", 20, "Start your first book on Authora", "Start your first book", lambda p: p.projects == 0, _b2),
    LifecycleStep("bible", 60, "Build the Book Bible for your book", "Build the Book Bible", lambda p: p.books > 0 and p.bibles == 0, _b3),
    LifecycleStep(
        "first_chapter", 120, "Write the first chapter of your book", "Write the first chapter",
        lambda p: p.books > 0 and p.chapters == 0, _b4,
    ),
    LifecycleStep(
        "halfway", 240, "Keep the draft moving", "Keep the draft moving",
        lambda p: 0 < p.words < MAX_WORDS_FOR_NO_EXPORT, _b5,
    ),
    LifecycleStep(
        "export", 336, "Your manuscript is ready to export", "Your manuscript is ready to export",
        lambda p: p.words >= MAX_WORDS_FOR_NO_EXPORT and p.exports == 0, _b6,
    ),
    LifecycleStep(
        "published", 0, "Your first book is out — what happens next", "Your first book is out",
        lambda p: p.published > 0, _b7, event=True,
    ),
)

STEP_BY_KEY = {s.key: s for s in LIFECYCLE_STEPS}


# --------------------------------------------------------------------------
# planning: what is due right now for this customer
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Decision:
    step: LifecycleStep
    action: str  # send | skip


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def plan(
    progress: UserProgress,
    *,
    created_at: datetime,
    handled: Collection[str],
    now: datetime,
) -> list[Decision]:
    """Return every step whose time has come, in ladder order.

    ``handled`` holds the steps already closed (sent or skipped). A step whose
    delay has elapsed but whose condition is false is returned with action
    ``skip`` so the ledger records it and the sweep stops revisiting it.
    """
    created_at, now = _aware(created_at), _aware(now)
    decisions: list[Decision] = []
    for step in LIFECYCLE_STEPS:
        if step.key in handled:
            continue
        if step.event and not step.when(progress):
            continue  # not reached yet: not due, and not a skip
        if now < created_at + timedelta(hours=step.delay_hours):
            continue
        # A published book ends the ladder: never nudge somebody who shipped.
        if progress.published and step.key != "published":
            decisions.append(Decision(step, SKIPPED))
            continue
        decisions.append(Decision(step, SENT if step.when(progress) else SKIPPED))
    return decisions


# --------------------------------------------------------------------------
# delivery and the ledger
# --------------------------------------------------------------------------
async def _deliver(to: str, subject: str, text: str, html: str) -> bool:
    """Transport boundary. Patched in tests; never reimplemented per step."""
    from authora.services.transactional_email import _send

    return await _send(to, subject, text, html)


async def _record(db: AsyncSession, user_id: UUID, step: str, status: str, detail: str | None, now: datetime) -> None:
    """Upsert the ledger row for (user, step) — a failure is retried, not duplicated."""
    existing = (
        await db.execute(
            select(LifecycleEmailLog).where(LifecycleEmailLog.user_id == user_id, LifecycleEmailLog.step == step)
        )
    ).scalar_one_or_none()
    if existing is None:
        db.add(
            LifecycleEmailLog(
                user_id=user_id,
                step=step,
                status=status,
                detail=detail,
                sent_at=now if status == SENT else None,
            )
        )
    else:
        existing.status = status
        existing.detail = detail
        existing.sent_at = now if status == SENT else None
    await db.flush()


async def send_welcome_and_record(user_id: UUID, email: str, display_name: str | None) -> bool:
    """Send the immediate welcome and close ladder step 1 in the same breath.

    Called as a background task from registration. Without the ledger stamp the
    hourly sweep would treat the account as un-welcomed and send a duplicate.
    """
    from authora.database import async_session_factory
    from authora.services.transactional_email import send_welcome

    ok = False
    try:
        ok = await send_welcome(email, display_name)
    except Exception:  # noqa: BLE001 - registration must not fail on mail
        logger.exception("welcome email failed for %s", email)

    try:
        async with async_session_factory() as db:
            await _record(db, user_id, "welcome", SENT if ok else FAILED, "at registration", datetime.now(timezone.utc))
            await db.commit()
    except Exception:  # noqa: BLE001
        logger.exception("could not stamp lifecycle welcome for %s", user_id)
    return ok


async def handled_steps(db: AsyncSession, user_id: UUID) -> set[str]:
    rows = (
        await db.execute(
            select(LifecycleEmailLog.step).where(
                LifecycleEmailLog.user_id == user_id, LifecycleEmailLog.status.in_(CLOSED)
            )
        )
    ).scalars().all()
    return set(rows)


async def run_lifecycle_sweep(
    db: AsyncSession,
    *,
    now: datetime | None = None,
    limit: int = 500,
    user_ids: Sequence[UUID] | None = None,
) -> dict[str, Any]:
    """Advance every customer's ladder by at most one message.

    Returns counts plus a per-user detail list so a cron log shows exactly who
    was mailed and who was skipped, without querying the database afterwards.
    """
    now = _aware(now or datetime.now(timezone.utc))

    q = select(User.id, User.email, User.display_name, User.created_at).where(User.is_active.is_(True))
    if user_ids is not None:
        q = q.where(User.id.in_(list(user_ids)))
    users = (await db.execute(q.order_by(User.created_at).limit(limit))).all()

    result: dict[str, Any] = {"scanned": len(users), "sent": 0, "skipped": 0, "failed": 0, "details": []}
    for user_id, email, display_name, created_at in users:
        handled = await handled_steps(db, user_id)
        progress = await collect_progress(db, user_id)
        name = _greeting(display_name or "")

        sent_this_run = False
        for decision in plan(progress, created_at=created_at, handled=handled, now=now):
            step = decision.step
            if decision.action == SKIPPED:
                await _record(db, user_id, step.key, SKIPPED, "not applicable", now)
                result["skipped"] += 1
                result["details"].append({"user": email, "step": step.key, "status": SKIPPED})
                continue
            if sent_this_run:  # one message per customer per run
                break
            text, html = step.build(progress, name)
            ok = False
            try:
                ok = await _deliver(email, step.subject, text, html)
            except Exception:  # noqa: BLE001 - mail must never break the sweep
                logger.exception("lifecycle email failed: %s / %s", step.key, email)
            await _record(db, user_id, step.key, SENT if ok else FAILED, None if ok else "delivery returned False", now)
            result["sent" if ok else "failed"] += 1
            result["details"].append({"user": email, "step": step.key, "status": SENT if ok else FAILED})
            sent_this_run = True

    await db.flush()
    logger.info(
        "lifecycle_sweep_completed",
        extra={"scanned": result["scanned"], "sent": result["sent"], "skipped": result["skipped"], "failed": result["failed"]},
    )
    return result
